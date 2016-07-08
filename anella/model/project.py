# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client, ANELLA_SECTORS
from service import ServiceDescription, GenericService, CloudService
from scontext import SContext

CREATED=0
SAVED=1
PENDING=2
CONFIRMED=3
PROVISIONED=4
RUNNING=5
# STOPPED=6
DEPLOYED=6
# FAILED=9
# ENDED=10

STATUS = (
    ( CREATED,		u'CREATED' ),
    ( SAVED,		u'SAVED' ),
    ( PENDING,	 	u'PENDING' ),
    ( CONFIRMED, 	u'CONFIRMED' ),
    ( PROVISIONED, 	u'PROVISIONED' ),
    ( RUNNING, 		u'RUNNING' ),
    ( DEPLOYED, 	u'DEPLOYED' ),
)

STATES = [status[1] for status in STATUS]

ROLES = (
    ( 'admin', 'Project administrator' ),
    ( 'client', 'Project client' ),
    ( 'provider', 'Project provider' ),
)


class SProject(Document, Base):
    """
    A Service when included in a Project whih its associated status and deployment info.
    """
    meta = {'allow_inheritance': True, 'collection': 'sprojects'}

    service = ReferenceField(ServiceDescription)
    project = ReferenceField('Project')
    provider = ReferenceField('Partner')
    context_type = StringField()
    context = DictField() # ReferenceField(SContext)
    status = IntField(choices=STATUS, default=CREATED)
    
    def get_client(self):
        return self.project.client

    client = property(get_client)

#     def get_provider(self):
#         return self.service.provider

#     provider = property(get_provider)

    def __init__(self, project, service, context_type, context=None, status=CREATED, **kwargs):
        super(SProject, self).__init__( project=project, service=service, 
                                context_type=context_type, context=context, status=status, **kwargs)
        self.provider=self.service.provider

    def ask_confirm(self):
        assert self.status==SAVED
        self.status=PENDING
        self.save()

    def confirm(self):
        """
        - sendmail provider
        """
        assert self.status<CONFIRMED
        self.status=CONFIRMED
        self.save()

    def save(self, *args, **kwargs):
        if self.status==CREATED:
            self.status=SAVED
        return super(SProject,self).save(*args, **kwargs)

#     def create_instance(self, project):
#         assert self.status==CONFIRMED
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
    sector = StringField(choices=ANELLA_SECTORS)

    client = ReferenceField(Client)
    user_roles = DictField()
    services = ListField(ReferenceField(SProject))

#     def create_instances(self):
#         for service in self.services:
#             s_instance = service.create_instance(project=self)
#             self.instances.append( s_instance )
# 
#         self.status==CONFIRMED

    def get_status(self):
        # Services are items (not obj)
        if not self.services:
            return CREATED
        project_status = None
        for sproject in self.services:
            if project_status is None or sproject.status < project_status:
                project_status = sproject.status
                continue
            # some error
            break

        return project_status
            
    status = property(get_status)

    def get_state(self):
        status = self.get_status()
        return STATES[status]

    state = property(get_state)
