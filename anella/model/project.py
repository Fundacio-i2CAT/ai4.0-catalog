# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client
from service import ServiceDescription, GenericService, CloudService
from scontext import SContext

SERVICE_SAVED=0
SERVICE_PENDING=1
SERVICE_COMFIRMED=2

SERVICE_STATUS = (
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

class SProject(Document, Base):
    """
    A Service when included in a Project whih its associated status and deployment info.
    """
    meta = {'allow_inheritance': True, 'collection': 'sprojects'}

    service = ReferenceField(ServiceDescription)
    project = ReferenceField('Project')
    context = ReferenceField(SContext)
    status = IntField(choices=SERVICE_STATUS)
    
    def __init__(self, project, service, context=None):
        super(SProject, self).__init__()
        self.project=project
        self.service=service
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
class Instance(Document, Base):
    """
    A Service when included in a Project whih its associated status and deployment info.
    """
    meta = {'allow_inheritance': True, 'collection': 'instances'}

    service = ReferenceField(SProject)
    project = ReferenceField('Project')
    start_at = DateTimeField()
    end_at = DateTimeField()
    status = IntField(choices=SERVICE_STATUS)
    exit_status = IntField()
    exit_error = StringField()
    
    def __init__(self, project, service, context=None):
        super(Instance, self).__init__()
        self.project=project
        self.service=service
        self.context=context or {}
        self.status=0

    def ask_confirm(self):
        assert self.status==SERVICE_SAVED
        self.status=SERVICE_PENDING

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
    status = IntField(choices=PROJECT_STATUS)

    def create_instances(self):
        for service in self.services:
            s_instance = service.create_instance(project=self)
            self.instances.append( s_instance )

        self.status==PROJECT_COMFIRMED

