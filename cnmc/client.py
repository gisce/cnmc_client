# -*- coding: utf-8 -*-

from authlib.client import OAuth1Session
import os
import logging
            

CNCM_envs = {
    'prod': '',
    'staging': '',
}

class Client(object):

    def __init__(self, **kwargs):
        logging.info("Initializing CNCM Client")

        # Handle the key and the secret
        self.key = None
        if 'key' in kwargs:
            assert type(kwargs['key']) == str, "The key must be an string. Current type '{}'".format(type(kwargs['key']))
            self.key = kwargs['key']
        else:
            self.key = os.getenv('CNMC_CONSUMER_KEY')
        assert self.key, "The key is needed to initialize the CNCM connection"


        # Handle the key and the secret
        self.secret = None
        if 'secret' in kwargs:
            assert type(kwargs['secret']) == str, "The secret must be an string. Current type '{}'".format(type(kwargs['secret']))
            self.key = kwargs['secret']
        else:
            self.secret = os.getenv('CNMC_CONSUMER_SECRET')
        assert self.secret, "The secret is needed to initialize the CNCM connection"


        # Handle environment, df "prod"
        self.environment = "prod"
        if 'environment' in kwargs:
            assert type(kwargs['environment']) == str, "environment argument must be an string"
            assert kwargs['environment'] in CNCM_envs.keys(), "Provided environment '{}' not recognized in defined CNMC_envs {}".format(kwargs['environment'], str(FACE_ENVS.keys()))
            self.environment = kwargs['environment']

        self.session = OAuth1Session(self.key, self.secret)


    def method(self, method, resource, **kwargs):
        """
        Main method handler

        So far, ask the API and return a JSON representation of the response
        """
        response, content = self.client.request(resource, method, **kwargs)
        print (response)
        return response
        return result.json()


    def get(self, resource, **kwargs):
        """
        GET method, it trigger an API.get method consuming the desired resource
        """
        return self.method(method="get", resource=resource, **kwargs)
