# -*- coding: utf-8 -*-
from marshmallow import Schema, fields, post_load
from munch import Munch

## Base response Models and Schemas

class CNMC_Response(Munch):
    pass

class ResponseSchema(Schema):
    code = fields.Integer()
    result = fields.Dict()
    error = fields.Bool()

    @post_load
    def create_model(self, data):
        return CNMC_Response(**data)



## CNMC Test resource Models and Schemas

class CNMC_TestEntry(Munch):
    pass

class TestEntrySchema(Schema):
    mensaje = fields.Str()

    @post_load
    def create_model(self, data):
        return CNMC_TestEntry(**data)


class CNMC_Test(Munch):
    pass

class TestSchema(Schema):
    result = fields.Nested(TestEntrySchema, many=False)

    @post_load
    def create_model(self, data):
        return CNMC_Test(**data)



## CNMC List resource Models and Schemas

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
    descripcion = fields.Str(attribute="descripción")

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



class BytesIO_field(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return ''
        return value

class CNMC_File(Munch):
    pass

class FilesSchema(ResponseSchema):
    result = BytesIO_field()

    @post_load
    def create_model(self, data):
        return CNMC_File(**data)
