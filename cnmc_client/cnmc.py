# -*- coding: utf-8 -*-
from .base import BaseApi
from .exceptions import APIConfigError
from .constants import CNMC_ENVS
import logging
from requests_oauthlib import oauth1_session
from authlib.oauth1.rfc5849 import SIGNATURE_HMAC_SHA1

CNCM_envs = {
    'prod': 'https://api.cnmc.gob.es',
    'staging': 'https://apipre.cnmc.gob.es',
}
NULL_TOKEN = None


class CNMC_API(BaseApi):
    # Backward compatibility
    def __init__(self, key=None, secret=None, environment=None, **kwargs):
        logging.info("Initializing CNCM Client")

        # Backward compatibility
        if not 'auth_session' in kwargs:
            auth_session = oauth1_session.OAuth1Session(
            client_key=key, client_secret=secret,
            signature_method=SIGNATURE_HMAC_SHA1
            )
            if not key or not secret:
                raise APIConfigError("Missing key or secret")
            if not environment:
                environment = 'prod'
            if environment not in CNMC_ENVS:
                'Environ {} is not a valid. Allowed environs {}'.format(
                    environment, list(CNMC_ENVS.keys())
                )
            base_url = CNCM_envs[environment]
            super(CNMC_API, self).__init__(base_url, auth_session, "", "")
        else:
            super(CNMC_API, self).__init__(**kwargs)

    def get_NIF(self):
        """
        Get NIF from test API method

        It also support us to identify if session is established properly //as done by the oficial CNMC web client
        """
        response = self.get(resource="/test/v1/nif")
        assert response['code'] == 200, "Connection is not established properly '{}'. Review oauth configuraion".format(str(response))

        assert 'result' in response and 'empresa' in response['result'] and response['result']['empresa'][0]
        return response['result']['empresa'][0]
