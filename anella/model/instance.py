# -*- coding: utf-8 -*-

from mongoengine import *

from base import Base

class Instance(Document, Base):
    """
    A Service when included in a Project whih its associated status and deployment info.
    """
    meta = {'allow_inheritance': True, 'collection': 'instances'}

    sproject = ReferenceField('SProject')
    instance_id = StringField() # Id Orchestration instance

    start_at = DateTimeField()
    end_at = DateTimeField()
#     exit_status = IntField()
#     exit_error = StringField()
    
    def get_project(self):
        return self.sproject.project

    def get_client(self):
        return self.sproject.project.client

    def get_service(self):
        return self.sproject.service

    def get_provider(self):
        return self.sproject.service.provider

    project = property(get_project)
    client = property(get_client)
    service = property(get_service)
    provider = property(get_provider)
