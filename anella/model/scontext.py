# -*- coding: utf-8 -*-

import json
from jsonschema import validate

from mongoengine import *

from base import Base
from anella.utils import resolve_parameters

_context_types = {}

def register_context_type(name,cls):
    _context_types[name]=cls

def get_context_type(cls):
    for n,t in _context_types.items():
        if cls==t:
            return n

def get_context_cls(name):
    return _context_types[name]


class SContext(Document, Base):
    """
    A Service when included in a Project whih its associated status and deployment info.
    """
    # Class level attrs
    schema = None
    schema_file_name = ''

    meta = {'allow_inheritance': True, 'collection': 'scontexts'}

    name = StringField(max_length=40, required=True, unique=True)
    description = StringField()
    context_type = StringField(required=True) # Dynamic/Hardcored? choices=CONTEXT_TYPES, default='generic')
    context = DictField()


    @classmethod
    def load_schema(cls,file_name=None):
        """ Expects caller manage exceptions
        """
        if file_name:
            cls.schema_file_name=file_name

        with open(cls.schema_file_name, 'rt') as fp:
            schema=json.loads(fp.read())
            cls.schema = schema

 
    def validate_context(self, properties=None):
        context = properties or self.context
        assert context and self.schema
 
        try:
            validate(context, self.schema)
            return True
        except ValidationError,e:
            return False
 

    def resolve_parameters(self, properties=None):
        """
        Tries to resolve parameters in self.properties, if any, 
        using additional optional properties probably coming from a service
        """
        return resolve_parameters(self.context, properties)


# register_context_type('systemd',SContext)
# register_context_type('docker',SContext)
