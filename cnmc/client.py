# -*- coding: utf-8 -*-

from .cnmc import CNMC_API
from .models import ListSchema
import os

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


    def list(self, status="DISPONIBLE", date_start=None, date_end=None):
        """
        List downloaded files or files able to be downloaded, with the capacity of filter it by:
        - >= start_date
        - <= end_date
        - status in ["DISPONIBLE", "DESCARGADO"]

        See https://documentacion.cnmc.es/doc/display/APIPUB/consultar
        """
        params = {
            "idProcedimiento": "2",
            "nifEmpresa": "XXXXXXX",
            "estado": status,
        }

        if date_start:
            params['fechaDesde'] = date_start

        if date_end:
            params['fechaHasta'] = date_start

        return self.API.post(resource="/consultar", params=params)
