from __future__ import unicode_literals
import socket

DEFAULT_TIMEOUT = socket.getdefaulttimeout()

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