# -*- coding: utf-8 -*-
from __future__ import (absolute_import)

from cnmc_client import Client

config = {
    'environment': 'prod'
}

LIST_OF_CUPS = ["ES0021000000228141PR", "ES0021000002097098PR", "ES0021000003589973DS"]
LIST_OF_FILE_TYPES = ["SIPS2_PS_ELECTRICIDAD", "SIPS2_CONSUMOS_ELECTRICIDAD", "SIPS2_PS_GAS", "SIPS2_CONSUMOS_GAS"]

client = Client(**config)

def fetch_SIPS(cups, file_type=LIST_OF_FILE_TYPES[0], as_csv=False):
    response = client.fetch(cups=cups, file_type=file_type, as_csv=as_csv)
    assert not response.error
    return response.result

def list_available_files():
    return client.list()

# Get SIPS file as bytes
SIPS_bytes = fetch_SIPS(cups=LIST_OF_CUPS)

# Get SIPS file as CSV reader
SIPS_csv = fetch_SIPS(cups=LIST_OF_CUPS, as_csv=True)

# Print each resultant element
for line in SIPS_csv:
    print (line)
