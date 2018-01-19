# -*- coding: utf-8 -*-

from .cnmc import CNMC_API
from .models import ListSchema, TestSchema, FilesSchema
import os
import io
import csv

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


    def test(self, message):
        """
        Test do not follow the default method
        """
        params = {
            "m": message,
        }
        response = self.API.get(resource="/test/v1/echoseguro", params=params)

        # Validate and deserialize the response
        schema = TestSchema()
        result = schema.load(response)

        if not result.errors:
            return result.data
        else:
            raise ValueError('Result deserialization is not performed properly for "{}"'.format(repr(result)))


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
        response = self.API.post(resource="/ficheros/v1/consultar", params=params)

        # Validate and deserialize the response
        schema = ListSchema()
        result = schema.load(response)

        if not result.errors:
            return result.data
        else:
            raise ValueError('Result deserialization is not performed properly for "{}"'.format(repr(result)))


    def fetch(self, cups, file_type, as_csv=False):
        """
        Fetch partial data for a list of CUPS

        Available file types:
        - SIPS2_PS_ELECTRICIDAD
        - SIPS2_CONSUMOS_ELECTRICIDAD
        - SIPS2_PS_GAS
        - SIPS2_CONSUMOS_GAS

        See https://documentacion.cnmc.es/doc/display/ICSV/API+de+consulta+individualizada

        Alternative, disabled right now: https://documentacion.cnmc.es/doc/display/ICSV/API+de+consulta+individualizada
        """

        assert type(cups) in [list]
        assert file_type in ["SIPS2_PS_ELECTRICIDAD", "SIPS2_CONSUMOS_ELECTRICIDAD", "SIPS2_PS_GAS", "SIPS2_CONSUMOS_GAS"]

        params = {
            "cups": ",".join(cups)
        }

        # Ask the API
        response = self.API.download(resource="/verticales/v1/SIPS/consulta/v1/{}.csv".format(file_type), params=params)

        # Return a csv reader if needed
        if as_csv:
            # Parse the downlaoded binary file as a csv
            csv_data = io.TextIOWrapper(response['result'])
            response['result'] = csv.reader(csv_data, delimiter=",", quotechar='"')

        # Validate and deserialize the response
        schema = FilesSchema()
        result = schema.load(response)

        if not result.errors:
            return result.data
        else:
            raise ValueError('Fetch result deserialization is not performed properly for "{}"'.format(repr(result)))


        return response


    def download(self, filename):
        """
        Download

        See https://documentacion.cnmc.es/doc/display/ICSV/API+de+consulta+individualizada

        Alternative, disabled right now: https://documentacion.cnmc.es/doc/display/ICSV/API+de+consulta+individualizada
        """

        assert type(filename) == str

        # Ask the API
        response = self.API.get(resource="/ficheros/v1/descarga/{}".format(filename))
        return response
