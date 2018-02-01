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


    def _divide(self, amount, division):
        if amount == "":
            return None

        assert float(division) != 0, "Division must not be 0"
        
        return float(amount) / float(division)
        
    def _adapt_type_electricidad(self, line):
	return {
	    'der_acces_llano': self._divide(line['valorDerechosAccesoW'], 1000),
	    'data_ult_lect': line['fechaUltimaLectura'],
	    'primera_vivienda': line['esViviendaHabitual'], #OJUT
	    'data_ult_canv': line['fechaUltimoCambioComercializador'],
	    'cnae': line['CNAE'],
	    'tipo_pm': line['codigoClasificacionPS'],
	    'codigoTipoSuministro': '',
	    'codigoTarifaATREnVigor': '001',
	    'motivoEstadoNoContratable': line['motivoEstadoNoContratable'],
	    'codi_postal': line['codigoPostalPS'],
	    'data_alta': line['fechaAltaSuministro'],
	    'pot_cont_p1': self._divide(line['potenciasContratadasEnWP1'], 1000),
	    'pot_cont_p2': self._divide(line['potenciasContratadasEnWP2'], 1000),
	    'pot_cont_p3': self._divide(line['potenciasContratadasEnWP3'], 1000),
	    'pot_cont_p4': self._divide(line['potenciasContratadasEnWP4'], 1000),
	    'pot_cont_p5': self._divide(line['potenciasContratadasEnWP5'], 1000),
	    'pot_cont_p6': self._divide(line['potenciasContratadasEnWP6'], 1000),
	    'data_ulti_mov': line['fechaUltimoMovimientoContrato'],
	    'pot_max_puesta': self._divide(line['potenciaMaximaAPMW'], 1000),
	    'der_extensio': self._divide(line['valorDerechosExtensionW'], 1000),
	    'fianza': line['importeDepositoGarantiaEuros'],
	    'perfil_consum': line['tipoPerfilConsumo'], #OJUT!
	    'distri': line['nombreEmpresaDistribuidora'],
	    'pot_max_bie': self._divide(line['potenciaMaximaBIEW'], 1000),
	    'persona_fj': line['tipoIdTitular'], #OJUT
	    'ine_provincia': line['codigoProvinciaPS'],
	    'ine_municipio': line['municipioPS'],
	    'indicatiu_icp': line['codigoDisponibilidadICP'],
	    'informacion_impagos': line['informacionImpagos'],
	    'codigo_ps_contratable': line['codigoPSContratable'],
	}

        
        
    def adapt_data(self, data, file_type=LIST_OF_FILE_TYPES[0]):
	adapted = []
        for line in data:
            print (line)

            if file_type == "SIPS2_PS_ELECTRICIDAD":
                adaption = self._adapt_type_electricidad(line)

            print (adaption)
            return adaption 


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
