# -*- coding: utf-8 -*-
from __future__ import (absolute_import)

import cnmc_client
from pymongo import MongoClient
from sets import Set

config = {
    'environment': 'prod',
}

mongo_config = {
    'connection_url': 'localhost:27017',
    'db': 'db',
    'user': None,
    'password': None,
}

LIST_OF_FILE_TYPES = ["SIPS2_PS_ELECTRICIDAD", "SIPS2_CONSUMOS_ELECTRICIDAD", "SIPS2_PS_GAS", "SIPS2_CONSUMOS_GAS"]

def find_CUPS_by_zip(zipcode):
    assert type(zipcode) == str and len(zipcode) == 5, "Provided zipcode '{}' is not valid".format(zipcode)

    search_params = {
        'codi_postal': zipcode,
    }

    fields = {
        'name': 1,
    }

    cups = Set()
    for a_cups in collections['cups'].find(search_params, fields):
        cups.add(a_cups['name'])

    return cups

def fetch_SIPS(cups, file_type=LIST_OF_FILE_TYPES[0], as_csv=False):
    response = client.fetch(cups=cups, file_type=file_type, as_csv=as_csv)
    assert not response.error
    return response.result


# Initialize CNMC Client
client = cnmc_client.Client(**config)

# Initialize MongoDB collections
mongo = MongoClient("mongodb://" + mongo_config['connection_url'])
collections = {
    'cups': mongo[mongo_config['db']].giscedata_sips_ps,
    'consumptions': mongo[mongo_config['db']].giscedata_sips_consums,

    'destination_cups': mongo[mongo_config['db']].giscedata_sips_ps_fmtjul16,
    'destination_consumptions': mongo[mongo_config['db']].giscedata_sips_consums_fmtjul16,
}

cups_list = find_CUPS_by_zip("42100")

SIPS_csv = fetch_SIPS(cups=cups_list, as_csv=True)

for line in SIPS_csv:
    print (line)

