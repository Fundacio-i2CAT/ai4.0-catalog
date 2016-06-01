# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client, ANELLA_SECTORS

SERVICE_TYPES = (
    ('generic', u'Generic Service' ),
    ('cloud', u'Cloud Service' ),
)

_service_types = {}

def register_service_type(name,cls):
    _service_types[name]=cls

def get_service_type(cls):
    for n,t in _service_types.items():
        if cls==t:
            return n

def get_service_cls(name):
    return _service_types[name]

class ServiceDescription(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'services'}

    # Collection fields
    name = StringField(max_length=40, required=True, unique=True)
    summary = StringField(max_length=120)
    description = StringField()
    service_type = StringField(choices=SERVICE_TYPES, default='generic')

    provider = ReferenceField(Partner)
    keywords = ListField(StringField(max_length=40))
    sectors = ListField(StringField(choices=ANELLA_SECTORS))

    link = URLField()
    logo = FileField()

#     images = EmbeddedDocumentListField(EmbeddedDocument)
#     bootstrap_script = StringField()

#     def to_json(self):
#         return dict(name=self.name, summary=self.summary, provider=self.provider.id, )

#     @classmethod
#     def from_json(cls, data):
#         service = cls(name=data['name'], summary=data['summary'])
#         service.provider = Partner.objects.get(id=data['provider'])


class GenericService(ServiceDescription):
    type_name = 'Generic'  # A type name to use in UI
    scheme = 'service-scheme.json'

class CloudService(ServiceDescription):
    type_name = 'Cloud'  # A type name to use in UI
    scheme = 'cloud-service-scheme.json'

    service_type = StringField(choices=SERVICE_TYPES, default='cloud')

register_service_type('generic',GenericService)
register_service_type('cloud',CloudService)


class Credential(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'credentials'}

    # Collection fields

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

