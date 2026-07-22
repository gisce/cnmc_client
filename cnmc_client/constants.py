from __future__ import unicode_literals
import socket

CNMC_ENVS = {
    "prod": "https://api.cnmc.gob.es",
    "staging": "https://apipre.cnmc.gob.es",
}

AVAILABLE_FILE_STATES = ["DISPONIBLE", "DESCARGADO"]
CUPS_CHUNK_SIZE = 10

SIPS_TYPES = {
    "SIPS2_PS_ELECTRICIDAD", "SIPS2_CONSUMOS_ELECTRICIDAD",
    "SIPS2_PS_GAS", "SIPS2_CONSUMOS_GAS"
}

API_MODES = {"catalogo", "carga", "ficheros", "test"}

API_VERSIONS = {"v1", "v2"}

class DEFAULTS:
    TIMEOUT =  socket.getdefaulttimeout()
    API_VERSION = "v1"
    API_ENV = "prod"
    API_MODE = "ficheros"
