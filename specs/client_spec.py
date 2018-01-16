# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr

import logging
logging.basicConfig(level=logging.DEBUG)

from cnmc import Client

fixtures_path = 'specs/fixtures/cnmc/'

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

        with context('list of pending files'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('list.yaml'):
                    response = self.client.list()
                    
                    assert response

                    print (response)
                    for element in response.result:
                        print (element.nombre, element.estado, element.tipoFichero, element.uriDescargas)
