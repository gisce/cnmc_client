# -*- coding: utf-8 -*-

import oauth2 as oauth
import logging

CNCM_envs = {
    'prod': '',
    'staging': '',
}

class Client(object):

    def __init__(self, **kwargs):
        logging.info("Initializing CNCM Client")

        # Handle environment, df "prod"
        self.environment = "prod"
        if 'environment' in kwargs:
            assert type(kwargs['environment']) == str, "environment argument must be an string"
            assert kwargs['environment'] in CNCM_envs.keys(), "Provided environment '{}' not recognized in defined CNMC_envs {}".format(kwargs['environment'], str(FACE_ENVS.keys()))
            self.environment = kwargs['environment']

        self.consumer = oauth.Consumer(key="your-twitter-consumer-key", secret="your-twitter-consumer-secret")

        self.client = oauth.Client(self.consumer)



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
