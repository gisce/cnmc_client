# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr
import io

import logging
logging.basicConfig(level=logging.DEBUG)

from cnmc_client import CNMC_API

fixtures_path = 'specs/fixtures/cnmc/'

spec_VCR = vcr.VCR(
    record_mode='all',
    cassette_library_dir=fixtures_path
)


config = {
    'key': 'the_key',
    'secret': 'the_secret',
}

scope = {
    "download": {
        "url": "/verticales/v1/SIPS/consulta/v1/SIPS2_PS_ELECTRICIDAD.csv?cups=ES0021000000228141PR"
    }
}

expected = {
    'NIF': 'the_nif',
}

with description('A new'):
    with before.each:
        with spec_VCR.use_cassette('init.yaml'):
            self.config = config
            self.expected = expected
            self.api = CNMC_API(**config)

    with context('CNMC API'):
        with context('initialization'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('init.yaml'):
                    result = self.api.get_NIF()
                    assert type(result) == str, "NIF format is not the expected (str)"
                    assert result == expected['NIF'], "NIF is not the expected one"

        with context('interaction'):
            with it('must work while downloading a file'):
                with spec_VCR.use_cassette('download.yaml'):
                    the_file = scope['download']['url']
                    response = self.api.download(resource=the_file)

                    assert isinstance(response['result'], io.BytesIO)
