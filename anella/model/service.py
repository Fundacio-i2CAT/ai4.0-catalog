# -*- coding: utf-8 -*-

from mongoengine import *

from common import Base
from partner import Partner, Provider, Client, ANELLA_SECTORS


class ServiceDescription(Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'services'}

    # Collection fields
    name = StringField(max_length=40, required=True, unique=True)
    summary = StringField(max_length=120)
    description = StringField()

    provider = ReferenceField(Partner)
    images = EmbeddedDocumentListField(EmbeddedDocument)
    bootstrap_script = StringField()


class GenericService(ServiceDescription):
    type_name = 'Generic'  # A type name to use in UI
    scheme = 'service-scheme.json'

class CloudService(ServiceDescription):
    type_name = 'Cloud'  # A type name to use in UI
    scheme = 'cloud-service-scheme.json'


class Credential(Base):
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

