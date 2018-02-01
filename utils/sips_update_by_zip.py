# -*- coding: utf-8 -*-
from __future__ import (absolute_import)

import cnmc_client
from pymongo import MongoClient
from sets import Set

import click

# Available SIPS file types and related destination collection
FILE_TYPES = {
    "SIPS2_PS_ELECTRICIDAD": "destination_ps",
    "SIPS2_CONSUMOS_ELECTRICIDAD": "destination_consumptions",
    #"SIPS2_PS_GAS": None,
    #"SIPS2_CONSUMOS_GAS": None,
}
LIST_OF_FILE_TYPES = list(FILE_TYPES)

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

	    'destination_ps': mongo[mongo_config['db']].giscedata_sips_ps_fmtjul16,
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
            'name': line['cups'],
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

        
    def _adapt_type_consumos(self, line):
	return {
            'name': line['cups'],
	    'data_inicial': line['fechaInicioMesConsumo'],
	    'data_final': line['fechaFinMesConsumo'],
	    'tarifa': line['codigoTarifaATR'],
	    'activa_1': self._divide(line['consumoEnergiaActivaEnWhP1'], 1000),
	    'activa_2': self._divide(line['consumoEnergiaActivaEnWhP2'], 1000),
	    'activa_3': self._divide(line['consumoEnergiaActivaEnWhP3'], 1000),
	    'activa_4': self._divide(line['consumoEnergiaActivaEnWhP4'], 1000),
	    'activa_5': self._divide(line['consumoEnergiaActivaEnWhP5'], 1000),
	    'activa_6': self._divide(line['consumoEnergiaActivaEnWhP6'], 1000),
	    'reactiva_1': self._divide(line['consumoEnergiaReactivaEnVArhP1'], 1000),
	    'reactiva_2': self._divide(line['consumoEnergiaReactivaEnVArhP2'], 1000),
	    'reactiva_3': self._divide(line['consumoEnergiaReactivaEnVArhP3'], 1000),
	    'reactiva_4': self._divide(line['consumoEnergiaReactivaEnVArhP4'], 1000),
	    'reactiva_5': self._divide(line['consumoEnergiaReactivaEnVArhP5'], 1000),
	    'reactiva_6': self._divide(line['consumoEnergiaReactivaEnVArhP6'], 1000),
	    'potencia_1': self._divide(line['potenciaDemandadaEnWP1'], 1000),
	    'potencia_2': self._divide(line['potenciaDemandadaEnWP2'], 1000),
	    'potencia_3': self._divide(line['potenciaDemandadaEnWP3'], 1000),
	    'potencia_4': self._divide(line['potenciaDemandadaEnWP4'], 1000),
	    'potencia_5': self._divide(line['potenciaDemandadaEnWP5'], 1000),
	    'potencia_6': self._divide(line['potenciaDemandadaEnWP6'], 1000),
	    'tipo_lectura': line['codigoTipoLectura'], #OJUT
	}
        
        
    def adapt_data(self, data, file_type=LIST_OF_FILE_TYPES[0]):
        """ 
        Adapt incoming SIPS data based on file type and configured requirements

        :param data: an iterable list/CSVReader of dict / DictReader
        :param file_type: the type of data
        :return: list of dict with the adapted data
        """ 
	adapted = []
        for line in data:
            adaption = {
                'SIPS2_PS_ELECTRICIDAD': self._adapt_type_electricidad,
                'SIPS2_CONSUMOS_ELECTRICIDAD': self._adapt_type_consumos,
            }[file_type](line)



@click.command()
@click.option('--host', default='localhost', help='MongoDB host')
@click.option('--port', default='27017', help='MongoDB port', type=click.INT)
@click.option('--user', default=None, help='MongoDB user')
@click.option('--password', default=None, help='MongoDB password')
@click.option('--database', default='database', help='MongoDB database')
@click.option('--cnmc', default='prod', help='CNMC environment')
@click.argument('zipcode', type=click.STRING)
@click.argument('file_type', type=click.Choice(LIST_OF_FILE_TYPES))
def main(zipcode, host, port, user, password, database, file_type, cnmc):
    cnmc_config = {
	'environment': 'cnmc',
    }

    mongo_config = {
	'connection_url': "{}:{}".format(host, port),
	'db': database,
	'user': user,
	'password': password,
    }

    utils = CNMC_Utils(cnmc_config, mongo_config)

    cups_list = utils.find_CUPS_by_zip(zipcode)
    SIPS_files = utils.fetch_SIPS(cups=cups_list[:3], as_csv=True, file_type=file_type)
    
    for a_file in SIPS_files:
        if a_file.error:
            continue

        SIPS_csv = a_file.result

        utils.adapt_data(data=SIPS_csv, file_type=file_type)



if __name__ == '__main__':
    main()
