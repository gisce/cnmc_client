# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr

import logging
logging.basicConfig(level=logging.DEBUG)

from cnmc import CNMC_API

fixtures_path = 'specs/fixtures/cnmc/'

spec_VCR = vcr.VCR(
    record_mode='all',
    cassette_library_dir=fixtures_path
)

config = {
    'key': 'the_key',
    'secret': 'the_secret',
}

expected = {
}

with description('A new'):
    with before.each:
        with spec_VCR.use_cassette('init.yaml'):
            self.config = config
            self.expected = expected
            self.client = CNMC_API(**config)

    with context('CNMC API'):
        with context('initialization'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('init.yaml'):
                    result = self.client.test(message="ROLF")
                    print (result)