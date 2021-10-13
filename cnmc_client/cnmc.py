# -*- coding: utf-8 -*-

import socket
import httplib
import oauth.oauth as oauth
import urllib
import json
import logging
from io import BytesIO

CNCM_envs = {
    'prod': 'https://api.cnmc.gob.es',
    'staging': 'https://apipre.cnmc.gob.es',
}
NULL_TOKEN = None


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
        self.environment = "prod"
        if not environment:
            if 'environment' in kwargs:
                assert type(kwargs['environment']) == str, "environment argument must be an string"
                assert kwargs['environment'] in CNCM_envs.keys(), "Provided environment '{}' not recognized in defined CNMC_envs {}".format(kwargs['environment'], str(FACE_ENVS.keys()))
                self.environment = kwargs['environment']

        self.url = CNCM_envs[self.environment]

    def get_NIF(self):
        """
        Get NIF from test API method

        It also support us to identify if session is established properly //as done by the oficial CNMC web client
        """
        response = self.get(resource="/test/v1/nif")
        assert response['code'] == 200, "Connection is not established properly '{}'. Review oauth configuraion".format(str(response))

        assert 'result' in response and 'empresa' in response['result'] and response['result']['empresa'][0]
        return response['result']['empresa'][0]

    def method(self, method, resource, download=False, **kwargs):
        """
        Main method handler

        Fetch the requested URL with the requested action through the OAuth session and return a JSON representeation of the response with the resultant code
        """
        url = self.url + resource
        from urlparse import urlparse
        parsed = urlparse(url)
        params = kwargs.get('params', None)
        timeout = kwargs.get('timeout', socket._GLOBAL_DEFAULT_TIMEOUT)
        consumer = oauth.OAuthConsumer(self.key, self.secret)
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            consumer, token=NULL_TOKEN, http_method=method,http_url=url,
            parameters=params
        )
        oauth_request.sign_request(signature_method_hmac_sha1, consumer, NULL_TOKEN)
        connection = httplib.HTTPSConnection(
            "%s:%d" % (parsed.hostname, parsed.port or 443),
            timeout=timeout
        )
        if method == 'GET' and params:
            resource +='?{}'.format(
                urllib.urlencode(params)
            )
        connection.request(method, resource, headers=oauth_request.to_header())  
        response = connection.getresponse()
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
                'message': str(response),
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
