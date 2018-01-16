from marshmallow import Schema, fields, post_load
from munch import Munch

class CNMC_Response(Munch):
    pass

class ResponseSchema(Schema):
    code = fields.Integer()
    result = fields.Dict()
    error = fields.Bool()

    @post_load
    def create_model(self, data):
        return CNMC_Response(**data)



class CNMC_ListEntry(Munch):
    pass

class ListEntrySchema(Schema):
    uuid = fields.Str()
    idProcedimiento = fields.Integer()
    nifEmpresa = fields.Str()
    numeroBytes = fields.Integer()
    tipoFichero = fields.Str()
    estado = fields.Str()
    mime = fields.Str()
    nombre = fields.Str()
    hash = fields.Str()
    fechaDisponibilidad = fields.Str()
    fechaCaducidad = fields.Str()
    uriDescargas = fields.Str()
    descripción = fields.Str()

    @post_load
    def create_model(self, data):
        return CNMC_ListEntry(**data)



class CNMC_List(Munch):
    pass

class ListSchema(ResponseSchema):
    result = fields.Nested(ListEntrySchema, many=True)

    @post_load
    def create_model(self, data):
        return CNMC_List(**data)
