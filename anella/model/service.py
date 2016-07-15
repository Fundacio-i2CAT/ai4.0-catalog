# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client, ANELLA_SECTORS

# TODO: Service types should be dynamic and use as options to validate field

_service_types = {}

def register_service_type(name,cls, des):
    _service_types[name]=(cls,des)

def get_service_type(cls):
    for n,t in _service_types.items():
        if cls==t[0]:
            return n

def get_service_cls(name):
    return _service_types[name]

def get_service_types():
    return _service_types.items()

class ServiceDescription(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'services',
            'indexes': ['name', ] }

    # Collection fields
    name = StringField(max_length=40, required=True, unique=True)
    summary = StringField(max_length=120)
    description = StringField()
    service_type = StringField(default='app')

    provider = ReferenceField(Partner)
    reference = StringField(max_length=50)
    keywords = ListField(StringField(max_length=40))
    sectors = ListField(StringField(choices=ANELLA_SECTORS))

    link = URLField()
    logo = ImageField()

    properties = DictField()

#     images = EmbeddedDocumentListField(EmbeddedDocument)
#     bootstrap_script = StringField()


class AppService(ServiceDescription):
    type_name = 'App'  # A type name to use in UI
    scheme = 'service-scheme.json'

class ISService(ServiceDescription):
    type_name = 'Infrastructure'  # A type name to use in UI
    scheme = 'cloud-service-scheme.json'

    service_type = StringField(default='iss')

register_service_type('app', AppService, 'App')
register_service_type('iss', ISService, 'Infraestructura')


class Image(EmbeddedDocument):
    """
    """
    # meta = {'allow_inheritance': True, 'collection': 'images'}
    meta = {'allow_inheritance': True}

    type_name = 'Generic'  # A type name to use in UI
    scheme = 'resource-scheme.json'

    # Collection fields
    name = StringField(max_length=40, required=True, unique=True)
    public = BooleanField( default=True )

class VMImage(Image):
    type_name = 'vm_image'  

    url = URLField()

class DockerImage(Image):
    """
    Considering a public image in Docker hub for now.
    """
    type_name = 'Dockerfile'  

