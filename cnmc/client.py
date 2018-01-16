# -*- coding: utf-8 -*-

from .cnmc import CNMC_API
from .models import ListSchema
import os

AVAILABLE_FILE_STATES = ["DISPONIBLE", "DESCARGADO"]

class Client(object):
    def __init__(self, key=None, secret=None, environment=None):

        # Handle the key
        self.key = key
        if not key:
            self.key = os.getenv('CNMC_CONSUMER_KEY')
        assert self.key, "The key is needed to initialize the CNCM connection"

        # Handle the secret
        self.secret = secret
        if not secret:
            self.secret = os.getenv('CNMC_CONSUMER_SECRET')
        assert self.secret, "The secret is needed to initialize the CNCM connection"

        # Handle the env, by default prod
        self.environment = "prod"
        if environment:
            self.environment = environment

        self.API = CNMC_API(key=self.key, secret=self.secret, environment=self.environment)


    def list(self, status=None, date_start=None, date_end=None):
        """
        List downloaded files or files able to be downloaded, with the capacity of filter it by:
        - >= start_date
        - <= end_date
        - status in ["DISPONIBLE", "DESCARGADO"]

        See https://documentacion.cnmc.es/doc/display/APIPUB/consultar
        """

        # Set status = "DISPONIBLE" by default
        if not status:
            status = AVAILABLE_FILE_STATES[0]
        assert status in AVAILABLE_FILE_STATES

        params = {
            "idProcedimiento": "2",
            "nifEmpresa": self.API.NIF,
            "estado": status,
        }

        # Handle "from date" filter
        if date_start:
            params['fechaDesde'] = date_start

        # Handle "to date" filter
        if date_end:
            params['fechaHasta'] = date_start

        # Ask the API 
        response = self.API.post(resource="/consultar", params=params)

        # Validate and deserialize the response 
        schema = ListSchema()
        result = schema.load(response)

        if not result.errors:
            return result.data
        else:
            raise ValueError('Result deserialization is not performed properly for "{}"'.format(repr(result)))
