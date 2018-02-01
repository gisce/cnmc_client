# -*- coding: utf-8 -*-
from __future__ import (absolute_import)

import cnmc_client
from pymongo import MongoClient
from sets import Set

import click

LIST_OF_FILE_TYPES = ["SIPS2_PS_ELECTRICIDAD", "SIPS2_CONSUMOS_ELECTRICIDAD", "SIPS2_PS_GAS", "SIPS2_CONSUMOS_GAS"]

TARIFFS_OCSUM = {
    '001': "2.0A",
    '003': "3.0A",
    '004': "2.0DHA",
    '005': "2.1A",
    '006': "2.1DHA",
    '007': "2.0DHS",
    '008': "2.1DHS",
    '011': "3.1A",
    '012': "6.1",
    '013': "6.2",
    '014': "6.3",
    '015': "6.4",
    '016': "6.5"
}

class CNMC_Utils(object):
    def __init__(self, cnmc_config, mongo_config):
	self.client = cnmc_client.Client(**cnmc_config)

	# Initialize MongoDB collections
	mongo = MongoClient("mongodb://" + mongo_config['connection_url'])
	self.collections = {
	    'cups': mongo[mongo_config['db']].giscedata_sips_ps,
	    'consumptions': mongo[mongo_config['db']].giscedata_sips_consums,

	    'destination_cups': mongo[mongo_config['db']].giscedata_sips_ps_fmtjul16,
	    'destination_consumptions': mongo[mongo_config['db']].giscedata_sips_consums_fmtjul16,
	}

    def find_CUPS_by_zip(self, zipcode):
	assert type(zipcode) in [str, unicode] and len(zipcode) == 5, "Provided zipcode '{}' is not valid".format(zipcode)

	search_params = {
	    'codi_postal': zipcode,
	}

	fields = {
	    'name': 1,
	}

	cups = Set()
	for a_cups in self.collections['cups'].find(search_params, fields):
	    cups.add(a_cups['name'])

	return list(cups)

    def fetch_SIPS(self, cups, file_type=LIST_OF_FILE_TYPES[0], as_csv=False):
	return self.client.fetch_massive(cups=cups, file_type=file_type, as_csv=as_csv)


    def adapt_data(self, data):
	adapted = []
        for line in data:
            print (line)
            adaption_pattern = {
                'der_acces_llano': float(line['valorDerechosAccesoW'])/1000,
                'data_ult_lect': line['fechaUltimaLectura'],
                'primera_vivienda': line['esViviendaHabitual'],
                'data_ult_canv': line['fechaUltimoCambioComercializador'],
                'cnae': line['CNAE'],
                'tipo_pm': line['codigoClasificacionPS'],
                'codigoTipoSuministro': '',
                'codigoTarifaATREnVigor': '001',
                'motivoEstadoNoContratable': line['motivoEstadoNoContratable'],
                'codi_postal': line['codigoPostalPS'],
                'data_alta': line['fechaAltaSuministro'],
                #'': line[''],
            }
            print (adaption_pattern)
            return adaption_pattern 


@click.command()
@click.option('--host', default='localhost', help='MongoDB host')
@click.option('--port', default='27017', help='MongoDB port', type=click.INT)
@click.option('--user', default=None, help='MongoDB user')
@click.option('--password', default=None, help='MongoDB password')
@click.option('--database', default='database', help='MongoDB database')
@click.argument('zipcode', type=click.STRING)
def main(zipcode, host, port, user, password, database):
    cnmc_config = {
	'environment': 'prod',
    }

    mongo_config = {
	'connection_url': "{}:{}".format(host, port),
	'db': database,
	'user': user,
	'password': password,
    }

    utils = CNMC_Utils(cnmc_config, mongo_config)
    # Initialize CNMC Client

    cups_list = utils.find_CUPS_by_zip(zipcode)
    SIPS_files = utils.fetch_SIPS(cups=cups_list[:3], as_csv=True)
    
    for a_file in SIPS_files:
        if a_file.error:
            continue

        SIPS_csv = a_file.result

        utils.adapt_data(SIPS_csv)



if __name__ == '__main__':
    main()
