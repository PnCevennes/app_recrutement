#coding: utf8

import datetime
from collections import OrderedDict


def prepare_date(data):
    if not data: 
        return
    try:
        return datetime.datetime.strptime(data, '%Y-%m-%d')
    except ValueError:
        return datetime.datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%fZ')


def serializer(cls):
    if not hasattr(cls, '__fields_list__'):
        cls.__fields_list__ = []
    else:
        cls.__fields_list__ = cls.__fields_list__[:]
    for attr, field in cls.__dict__.items():
        if isinstance(field, Field):
            field.name = attr
            cls.__fields_list__.append(attr)
    return cls


class Field:
    def __init__(self, *,
            alias=None,
            checkfn=lambda x: True,
            preparefn=lambda x: x,
            serializefn=lambda x: x,
            default=None):
        self.name = None
        self.alias = alias
        self.serializefn = serializefn
        self.preparefn = preparefn
        self.checkfn = checkfn
        self.default = default

    def __set__(self, instance, value):
        value = self.preparefn(value)
        print(value)
        if not self.checkfn(value):
            instance.errors[self.name] = value
            raise ValueError
        setattr(instance.obj, self.alias or self.name, value)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        val = getattr(instance.obj, self.alias or self.name, self.default)
        return self.serializefn(val)


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors


class Serializer:
    def __init__(self, obj):
        self.obj = obj
        self.errors = {}

    def populate(self, data):
        errors = False
        for name, value in data.items():
            try:
                setattr(self, name, value)
            except ValueError as err:
                errors = True
                self.errors[name] = value
        if errors:
            raise ValidationError(self.errors)

    def set_fields(self, fields):
        self.__fields_list__ = fields

    def serialize(self, fields=None):
        if fields is None :
            return {field: getattr(self, field) for field in self.__fields_list__}
        else:
            out = OrderedDict()
            for field in fields:
                out[field] = getattr(self, field)
            return out


'''
@serializer
class TestSerializer(Serializer):
    #a = Field(serializefn=lambda x: x.strftime('%d/%m/%Y %H-%M-%S'))
    a = Field(serializefn=str)
    b = Field(alias='plop', serializefn=lambda x: x+5, default=10, checkfn=lambda x: 1<=x<=100)
    c = Field()
    d = Field()
'''
