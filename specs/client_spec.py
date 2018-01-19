# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr
import io
import csv
import logging
logging.basicConfig(level=logging.DEBUG)

from cnmc import Client

fixtures_path = 'specs/fixtures/client/'

spec_VCR = vcr.VCR(
    record_mode='new',
    cassette_library_dir=fixtures_path
)

config = {
#    'key': 'the_key',
#    'secret': 'the_secret',
}

expected = {
}

LIST_OF_CUPS = ["ES0021000000228141PR", "ES0021000002097098PR", "ES0021000003589973DS"]
LIST_OF_FILE_TYPES = ["SIPS2_PS_ELECTRICIDAD", "SIPS2_CONSUMOS_ELECTRICIDAD", "SIPS2_PS_GAS", "SIPS2_CONSUMOS_GAS"]

with description('A new'):
    with before.each:
        with spec_VCR.use_cassette('init.yaml'):
            self.config = config
            self.expected = expected
            self.client = Client(**config)

    with context('CNMC client'):
        with context('initialization'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('init.yaml'):
                    assert self.client

        """

        with context('test method'):
            with it('must work as expected'):
                with spec_VCR.use_cassette('test.yaml'):
                    message="this is just a test!"
                    response = self.client.test(message=message)

                    assert response and 'result' in response
                    assert 'mensaje' in response.result
                    assert response.result.mensaje == message


        with context('list of pending files'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('list.yaml'):
                    response = self.client.list()

                    assert response

                    print (response)
                    for element in response.result:
                        print (element.nombre, element.estado, element.tipoFichero, element.uriDescargas)
        """

        with context('reach files for some CUPS'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('fetch.yaml'):
                    the_cups = [ LIST_OF_CUPS[0] ]
                    the_type = LIST_OF_FILE_TYPES[0]

                    # Fetching the file as bytes
                    response = self.client.fetch(cups=the_cups, file_type=the_type)
                    print (type(response['result']))
                    assert isinstance(response['result'], io.BytesIO), "Fetch a file must return a BytesIO instance"

                    """
                    print (response)
                    for element in response.result:
                        print (element.nombre, element.estado, element.tipoFichero, element.uriDescargas)
                    """

        """
        with context('download of a file'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('download.yaml'):
                    response = self.client.list()
                    assert response

                    # Extract the filename from the URL
                    filename = str(response['result'][0].uriDescargas).split("/")[-1]

                    # Ask the API to download it
                    response = self.client.download(filename=filename)
                    print (response)
                    assert response
        """
