# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base
from partner import Partner, Provider, Client, ANELLA_SECTORS
from service import ServiceDescription
from scontext import SContext

CREATED=0
SAVED=1
PENDING=2
CONFIRMED=3
PROVISIONED=4
RUNNING=5
# STOPPED=6
DEPLOYED=6
FAILED=7
DISABLED=8
UNKNOWN=9

STATUS = (
    ( CREATED,		u'CREATED' ),
    ( SAVED,		u'SAVED' ),
    ( PENDING,	 	u'PENDING' ),
    ( CONFIRMED, 	u'CONFIRMED' ),
    ( PROVISIONED, 	u'PROVISIONED' ),
    ( RUNNING, 		u'RUNNING' ),
    ( DEPLOYED, 	u'DEPLOYED' ),
    ( FAILED, 		u'FAILED' ),
    ( DISABLED, 	u'DISABLED' ),
    ( UNKNOWN, 	    u'UNKNOWN' )
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
    status = IntField(choices=STATUS, default=CREATED)
    consumer_params = DictField()
    runtime_param = DictField()

    def get_client(self):
        return self.project.client

    client = property(get_client)

    def __init__(self, project=None, service=None, status=CREATED, **kwargs):
        super(SProject, self).__init__( project=project, service=service, status=status, **kwargs)

    def ask_confirm(self):
        assert self.status==SAVED
        self.status=PENDING
        self.save()

    def confirm(self):
        """
        - sendmail provider ?
        """
        assert self.status<CONFIRMED
        self.status=CONFIRMED
        self.save()

    def save(self, *args, **kwargs):
        if self.status==CREATED:
            self.status=SAVED
        return super(SProject,self).save(*args, **kwargs)

    def set_consumer_params(self, consumer_params):
        self.consumer_params['consumer_params'] = consumer_params


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

    def get_status(self):
        # Services are items (not obj)
        if not self.services:
            return CREATED
        project_status = None
        for sproject in self.services:
            if sproject.status == DISABLED:
                project_status = DISABLED
                break
          
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
