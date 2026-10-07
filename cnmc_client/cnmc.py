# -*- coding: utf-8 -*-

import socket
import httplib
import urllib
import base64
import json
import time
import logging
from io import BytesIO
from urlparse import urlparse

CNCM_envs = {
    'prod': 'https://api.cnmc.gob.es',
    'staging': 'https://apipre.cnmc.gob.es',
}

TOKEN_PATH = '/oauth2/token'
TOKEN_SCOPE = 'read'
# Seconds before the real expiration when the token is considered expired
TOKEN_EXPIRY_MARGIN = 30

PROFILE_RESOURCE = '/api-oauth2/test/perfil'


class CNMC_API(object):

    def __init__(self, key=None, secret=None, environment=None, **kwargs):
        logging.info("Initializing CNCM Client")

        # Handle the key
        if not key:
            assert 'key' in kwargs
            key = kwargs['key']
        assert type(key) == str, "The key must be an string. Current type '{}'".format(type(key))
        self.key = key

        # Handle the secret
        if not secret:
            assert 'secret' in kwargs
            secret = kwargs['secret']
        assert type(secret) == str, "The key must be an string. Current type '{}'".format(type(secret))
        self.secret = secret

        # Handle environment, default value "prod"
        environment = environment or kwargs.get('environment') or 'prod'
        assert type(environment) == str, "environment argument must be an string"
        assert environment in CNCM_envs.keys(), "Provided environment '{}' not recognized in defined CNMC_envs {}".format(environment, str(CNCM_envs.keys()))
        self.environment = environment

        self.url = CNCM_envs[self.environment]

        # OAuth 2.0 token cache
        self._access_token = None
        self._token_expires_at = 0
        self._nif = None

    @property
    def NIF(self):
        if not self._nif:
            self._nif = self.get_NIF()
        return self._nif

    def get_NIF(self):
        """
        Get NIF from test API method

        It also support us to identify if session is established properly //as done by the oficial CNMC web client
        """
        response = self.get(resource=PROFILE_RESOURCE)
        assert response['code'] == 200, "Connection is not established properly '{}'. Review oauth configuraion".format(str(response))

        profile = response.get('result') or {}
        # Legacy /test/v1/nif format: {"empresa": ["NIF"]}
        if profile.get('empresa'):
            empresa = profile['empresa']
            return empresa[0] if isinstance(empresa, list) else empresa
        for key in ('nif', 'nifEmpresa', 'NIF'):
            if profile.get(key):
                return profile[key]
        raise ValueError("NIF not found in profile response '{}'".format(str(profile)))

    def _connection(self, url, timeout):
        parsed = urlparse(url)
        return httplib.HTTPSConnection(
            "%s:%d" % (parsed.hostname, parsed.port or 443),
            timeout=timeout
        )

    def fetch_token(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        Ask a new OAuth 2.0 access token using the client_credentials grant

        There is no refresh token, a new token is requested the same way when the previous one expires
        """
        credentials = base64.b64encode('{}:{}'.format(self.key, self.secret))
        headers = {
            'Authorization': 'Basic {}'.format(credentials),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        }
        body = urllib.urlencode({
            'grant_type': 'client_credentials',
            'scope': TOKEN_SCOPE,
        })
        connection = self._connection(self.url, timeout)
        connection.request('POST', TOKEN_PATH, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read()
        if response.status != 200:
            raise ValueError("OAuth2 token request failed with code '{}': {}".format(response.status, content))

        data = json.loads(content)
        self._access_token = data['access_token']
        self._token_expires_at = time.time() + int(data.get('expires_in', 0))
        return self._access_token

    def get_token(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        Return the current access token, asking a new one if missing or about to expire
        """
        if not self._access_token or time.time() >= self._token_expires_at - TOKEN_EXPIRY_MARGIN:
            self.fetch_token(timeout=timeout)
        return self._access_token

    def invalidate_token(self):
        self._access_token = None
        self._token_expires_at = 0

    def _do_request(self, method, url, path, body, headers, timeout):
        connection = self._connection(url, timeout)
        connection.request(method, path, body=body, headers=headers)
        return connection.getresponse()

    def method(self, method, resource, download=False, auth=True, **kwargs):
        """
        Main method handler

        Fetch the requested URL with the requested action using an OAuth 2.0 Bearer token and return a JSON representeation of the response with the resultant code

        Resource can be a path relative to the environment URL or an absolute URL. With auth=False no token is sent
        """
        if resource.startswith('http'):
            url = resource
        else:
            url = self.url + resource
        parsed = urlparse(url)
        path = parsed.path
        if parsed.query:
            path += '?{}'.format(parsed.query)

        params = kwargs.get('params', None)
        timeout = kwargs.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT)

        body = None
        headers = {}
        if params:
            encoded = urllib.urlencode(params)
            if method == 'GET':
                path += '{}{}'.format('&' if '?' in path else '?', encoded)
            else:
                body = encoded
                headers['Content-Type'] = 'application/x-www-form-urlencoded'

        if auth:
            headers['Authorization'] = 'Bearer {}'.format(self.get_token(timeout=timeout))
        response = self._do_request(method, url, path, body, headers, timeout)

        # Expired or invalid token: ask a new one and retry once
        if auth and response.status == 401:
            response.read()
            self.invalidate_token()
            headers['Authorization'] = 'Bearer {}'.format(self.get_token(timeout=timeout))
            response = self._do_request(method, url, path, body, headers, timeout)

        status_code = response.status
        if download:
            return {
                'code': response.status,
                'result': BytesIO(response.read()),
                'error': True if status_code >= 400 else False,
            }

        # Handle errors
        if status_code >= 400:
            return {
                'code': status_code,
                'error': True,
                'message': response.read(),
            }
        else:
            return {
                'code': status_code,
                'result': json.loads(response.read()),
                'error': False,
            }

    def get(self, resource, **kwargs):
        """
        GET method, it dispatch a session.get method consuming the desired resource
        """
        return self.method(method="GET", resource=resource, **kwargs)

    def post(self, resource, **kwargs):
        """
        POST method, it dispatch a session.get method consuming the desired resource
        """
        return self.method(method="POST", resource=resource, **kwargs)

    def download(self, resource, **kwargs):
        """
        GET method, it dispatch a session.get method consuming the desired resource
        """
        return self.method(method="GET", resource=resource, download=True, **kwargs)
