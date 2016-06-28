# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client
from service import ServiceDescription, GenericService, CloudService
from scontext import SContext

SERVICE_CREATED=0
SERVICE_SAVED=0
SERVICE_PENDING=1
SERVICE_COMFIRMED=2

SERVICE_STATUS = (
    ( SERVICE_CREATED,			u'Nou' ),
    ( SERVICE_SAVED,			u'Guardat' ),
    (	SERVICE_PENDING,	 	u'Pendent confirmar' ),
    ( SERVICE_COMFIRMED, 	u'Confirmat' ),
    ( 								2, 	u'Instanciat' ),
    ( 								3, 	u'Aturat' ),
    ( 								4, 	u'Finalitzat' ),
)

PROJECT_ROLES = (
    ( 'admin', 'Project administrator' ),
    ( 'client', 'Project client' ),
    ( 'provider', 'Project provider' ),
)

PROJECT_CREATED=0
PROJECT_SAVED=1
PROJECT_COMFIRMED=3
PROJECT_PROVISIONED=5
PROJECT_DEPLOYED=6
PROJECT_STARTED=7
PROJECT_STOPPED=8
PROJECT_FAILED=9
PROJECT_ENDED=10

PROJECT_STATUS = (
    ( PROJECT_CREATED, u'Nou' ),
    ( PROJECT_SAVED, u'Guardat' ),
    ( PROJECT_COMFIRMED, u'Confirmat' ),
    ( PROJECT_PROVISIONED, u'Provisioned' ),
    (	PROJECT_STARTED, u'Running' ),
    (	PROJECT_STOPPED, u'Aturat' ),
    (	PROJECT_FAILED, u'Fallat' ),
    (	PROJECT_ENDED, u'Finalitzat' ),
)

class SProject(Document, Base):
    """
    A Service when included in a Project whih its associated status and deployment info.
    """
    meta = {'allow_inheritance': True, 'collection': 'sprojects'}

    service = ReferenceField(ServiceDescription)
    project = ReferenceField('Project')
    context_type = StringField()
    context = DictField() # ReferenceField(SContext)
    status = IntField(choices=SERVICE_STATUS, default=SERVICE_CREATED)
    
    def get_client(self):
        return self.project.client

    def get_provider(self):
        return self.service.provider

    client = property(get_client)
    provider = property(get_provider)

    def __init__(self, project, service, context_type, context=None):
        super(SProject, self).__init__()
        self.project=project
        self.service=service
        self.context_type=context_type
        self.context=context
        self.status=0

    def ask_confirm(self):
        assert self.status==SERVICE_SAVED
        self.status=SERVICE_PENDING

    def confirm(self):
        """
        - sendmail provider
        """
        assert self.status==0
        self.status=1

#     def create_instance(self, project):
#         assert self.status==SERVICE_COMFIRMED
#         s_instance = Instance(service=self.service, project=self.project)
#         s_instance.save()
#         return s_instance
# 
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
    services = ListField(ReferenceField(SProject))
    status = IntField(choices=PROJECT_STATUS, default=PROJECT_CREATED)

    def create_instances(self):
        for service in self.services:
            s_instance = service.create_instance(project=self)
            self.instances.append( s_instance )

        self.status==PROJECT_COMFIRMED

