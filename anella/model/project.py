# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client
from service import ServiceDescription, GenericService, CloudService

SERVICE_COMFIRMED=1
SERVICE_STATUS = (
    ( 								0, u'Pendent confirmar' ),
    ( SERVICE_COMFIRMED, u'Confirmat' ),
    ( 								2, u'Instanciat' ),
    ( 								3, u'Aturat' ),
    ( 								4, u'Finalitzat' ),
)

PROJECT_ROLES = (
    ( 'admin', 'Project administrator' ),
    ( 'client', 'Project client' ),
    ( 'provider', 'Project provider' ),
)

PROJECT_COMFIRMED=3
PROJECT_STATUS = (
    ( 								0, u'Nou' ),
    ( 								1, u'Disseny' ),
    ( 								2, u'Pendent confirmar' ),
    ( PROJECT_COMFIRMED, u'Confirmat' ),
    ( 								4, u'Instanciat' ),
    ( 								5, u'Aturat' ),
    ( 								6, u'Finalitzat' ),
)

class ServiceContext(Document):
    """
    A Service when included in a Project whih its associated status and deployment info.
    """
    service = ReferenceField(ServiceDescription)
    project = GenericReferenceField()
    status = IntField(choices=SERVICE_STATUS)
    
    def __init__(self, service):
        super(ServiceContext, self).__init__(self)
        self.service=service
        self.status=0

    def confirm(self):
        assert self.status==0
        self.status=1

    def create_instance(self, project):
        assert self.status==SERVICE_COMFIRMED
        s_instance = ServiceInstance(service=self.service, project=project)
        s_instance.save()
        return s_instance


class Project(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'projects'}


    # Collection fields
    name = StringField(max_length=40, required=True, unique=True)
    summary = StringField(max_length=120)
    description = StringField()

    client = ReferenceField(Client)
    user_roles = DictField()
    services = ListField(ReferenceField(ServiceContext))
    status = IntField(choices=PROJECT_STATUS)

    def create_instances(self):
        for service in self.services:
            s_instance = service.create_instance(project=self)
            self.instances.append( s_instance )

        self.status==PROJECT_COMFIRMED

