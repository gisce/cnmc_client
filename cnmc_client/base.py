from __future__ import absolute_import, unicode_literals
from requests_oauthlib import oauth1_session
from authlib.oauth1.rfc5849 import SIGNATURE_HMAC_SHA1
from .exceptions import APIError, APIConfigError, APIUsageError
from .constants import CNMC_ENVS, DEFAULTS
from io import BytesIO
import logging
import json
import os
try:
    # Python 3
    from urllib.parse import urlparse, urljoin
except:
    # Python 2
    from urlparse import urlparse, urljoin


logging.basicConfig(level=logging.INFO)


class BaseApi(object):
    def __init__(self, base_url, auth_session, version=DEFAULTS.API_VERSION, mode=DEFAULTS.API_MODE):
        self.base_url = base_url
        self.auth_session = auth_session
        self.version = version
        self.mode = mode

    @staticmethod
    def join_url(base, *parts):
        url = base if base.endswith("/") else base + "/"
        for p in parts:
            url = urljoin(url, p if p.endswith("/") else p + "/")
        return url.rstrip("/")

    def _url(self, resource):
        return self.join_url(self.base_url, self.mode, self.version, resource)

    def _parsed_url(self, resource):
        return urlparse(self._url(resource))

    def method(self, method, resource, download=False, **kwargs):
        """
        Main method handler

        Fetch the requested URL with the requested action through the OAuth session and return a JSON representeation of the response with the resultant code
        """
        url = self._url(resource)
        params = kwargs.pop('params', None)
        timeout = kwargs.pop('timeout', DEFAULTS.TIMEOUT)

        headers = kwargs.pop("headers", {}) or {}
        headers.setdefault("Accept", "application/json")
        headers.setdefault("User-Agent", "cnmc-client/1.0")

        response = self.auth_session.request(
            method=method, url=url, params=params, timeout=timeout, headers=headers, **kwargs
        )

        status_code = response.status_code
        # return response
        if download:
            return {
                'code': response.status_code,
                'result': BytesIO(response.content),
                'error': True if status_code >= 400 else False,
            }

        # Handle errors
        if status_code >= 400:
            return {
                'code': status_code,
                'error': True,
                'message': response.text,
            }
        else:
            return {
                'code': status_code,
                'result': json.loads(response.content),
                'error': False,
            }


    def get(self, resource, **kwargs):
        """
        GET method, it dispatches a session.get method consuming the desired resource
        """
        return self.method(method="GET", resource=resource, **kwargs)

    def post(self, resource, **kwargs):
        """
        POST method, it dispatches a session.get method consuming the desired resource
        """
        return self.method(method="POST", resource=resource, **kwargs)

    def put(self, resource, **kwargs):
        """
        PUT method, it dispatches a session.get method consuming the desired resource
        """
        return self.method(method="PUT", resource=resource, **kwargs)

    def delete(self, resource, **kwargs):
        """
        DELETE method, it dispatches a session.get method consuming the desired resource
        """
        return self.method(method="DELETE", resource=resource, **kwargs)

    def download(self, resource, **kwargs):
        """
        GET method, it dispatches a session.get method consuming the desired resource
        """
        return self.method(method="GET", resource=resource, download=True, **kwargs)


class BaseApiClient(object):
    logger = logging.getLogger('cnmc_client')
    REQUIRED_PARAMS = ('key', 'secret')
    ENVIRON_MAPPING = {'key': 'CNMC_CONSUMER_KEY', 'secret': 'CNMC_CONSUMER_SECRET'}

    def check_required_params(self, raise_exception=True):
        missing_params = []
        for _param in self.REQUIRED_PARAMS:
            if not getattr(self, _param, False):
                missing_params.append(_param)

        if raise_exception and missing_params:
            raise APIConfigError("Missing params {}".format(missing_params))

        return missing_params

    def get_required_params_from_env_vars(self, param):
        try:
            return os.environ.get(self.ENVIRON_MAPPING[param], None)
        except KeyError:
            raise APIUsageError('{} has not environ variable mapping. {}'.format(param, self.ENVIRON_MAPPING))

    def __init__(self, key=None, secret=None, environment=None, timeout=None, api_class=BaseApi):
        self.API = None
        self.key = key or self.get_required_params_from_env_vars('key')
        self.secret = secret or self.get_required_params_from_env_vars('secret')
        self.environment = environment if environment is not None else 'prod'
        self.timeout = timeout
        self.api_class = api_class
        self.check_required_params(raise_exception=True)
        self.auth_session = oauth1_session.OAuth1Session(
            client_key=self.key, client_secret=self.secret,
            signature_method=SIGNATURE_HMAC_SHA1
        )
        self.setup_apis()

    def setup_apis(self):
        try:
            self.API = self.api_class(
                base_url=CNMC_ENVS[self.environment], auth_session=self.auth_session,
                # DUMMY API
                version="", mode=""
            )
        except KeyError:
            raise APIConfigError(
                'Environ {} is not a valid. Allowed environs {}'.format(
                    self.environment, list(CNMC_ENVS.keys())
                )
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.auth_session.close()



