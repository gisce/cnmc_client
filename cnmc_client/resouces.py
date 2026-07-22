from __future__ import unicode_literals

class UploadResources:
    """
    Docs: https://sede.cnmc.gob.es/documentacion/api-publico/carga
    """
    # GET/DELETE /carga/v1/cancelar_carga/<uuidCarga>
    CANCEL_UPLOAD = "cancelar_carga/"

    # GET/DELETE carga/v1/cancelar_fichero/<uuidUpload>
    CANCEL_FILE = "cancelar_fichero/"

    # PUT carga/v1/cargar_fichero_completo
    # ?nifPresentador=<nifPresentador>&nifEmpresa=<nifEmpresa>
    # &idProcedimiento=<idProcedimiento>&fechaEfecto=<fechaEfecto>
    # &tipoFichero=<tipoFichero>&nombreFichero=<nombreFichero>
    # &numeroBytes=<Tamaño del fichero>&hash=<>
    UPLOAD_FULL_FILE = "cargar_fichero_completo/"

    # GET carga/v1/confirmar_carga/<uuidCarga>
    CONFIRM_UPLOAD = "confirmar_carga/"

    # GET carga/v1/confirmar_subida_fichero/<uuidUpload>
    CONFIRM_FILE_UPLOAD = "confirmar_subida_fichero/"

    # GET carga/v1/consultar_estado_carga/<uuidCarga>
    CHECK_UPLOAD_STATE = "consultar_estado_carga/"

    # POST/PUT carga/v1/iniciar_carga
    # {"nifPresentador":"12345678Z", "nifEmpresa":"11111111H", "idProcedimiento": 1, "fechaEfecto":"2015-01-31"}
    START_UPLOAD = "iniciar_carga/"

    # POST/PUT carga/v1/iniciar_subida_fichero
    # {
    #   "uuidCarga": "550e8400-e29b-41d4-a716-446655440000", "tipoFichero": "SGDA",
    #   "nombreFichero": "mi_fichero_lopd.csv", "numeroBytes": 5678900000
    # }
    START_UPLOAD_FILE = "iniciar_subida_fichero/"

    # POST/PUT carga/v1/listar_cargas
    # {"nifEmpresa":"11111111H", "idProcedimiento": 12345, "estado":"INICIADA"}
    LIST_UPLOADS = "listar_cargas/"

    # GET carga/v1/listar_chunks_fichero/<uuidUpload>
    LIST_CHUNKS = "listar_chunks_fichero/"

    # POST/PUT carga/v1/subir_chunk_fichero/<uuidFichero>?numeroParte=<partNumber>&tamanoParte=<tamanoParte>
    UPLOAD_FILE_CHUNK = "subir_chunk_fichero/"







