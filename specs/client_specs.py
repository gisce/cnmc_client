# -*- coding: utf-8 -*-
from __future__ import (absolute_import)
import vcr

from cnmc import client

fixtures_path = 'specs/fixtures/cnmc/'

spec_VCR = vcr.VCR(
    record_mode='new_episodes',
    cassette_library_dir=fixtures_path
)

with description('A new'):
    with before.each:
        self.config = config
        self.expected = expected

    with context('CNMC client'):
        with context('initialization'):
            with it('must be performed as expected'):
                with spec_VCR.use_cassette('init.yaml'):
                    pass

