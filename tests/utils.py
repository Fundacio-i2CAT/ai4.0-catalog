
import os
import sys
import datetime
import unittest
import uuid

from mongoengine import connect, connection

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

from anella import configuration as cfg
from anella import utils
from anella import common

from anella.model.user import User
from anella.model.partner import Partner, Provider, Client, User, Contact, ANELLA_SECTORS
from anella.model.project import ServiceContext, Project
from anella.model.service import GenericService, CloudService
# from anella.model.service import VMImage, DockerImage

class DocLoader(object):

    def create_admin(self):
        self.user = User(email=cfg.admin__email, user_name=cfg.admin__user,
                         admin=True, staff=True)
        self.user.save()

    def create_provider(self):
        user = User(email='prov1@prov1.com')
        user.save()
        self.provider = Provider(name='prov1', 
                            contact = Contact(email='prov1@prov1.com'),
                            users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        self.provider.save()

    def create_client(self):
        user = User(email='client1@client1.com')
        user.save()
        self.client = Client(name='client1', 
                            contact = Contact(email='client1@client1.com'),
                            users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        self.client.save()

    def create_generic(self):
#         image = DockerImage(name='orambla/anella')
        self.generic = GenericService(name='service1',
                                 summary = "summary 1",
                                 description = "description 1",
                                 link = "http://link1.com",
                                 provider = self.provider,
                                 keywords= [ "storage" ],
                                 sectors= [ "industry" ],
#                                  images = [image,],
                                )
        self.generic.save()

    def create_cloud(self):
#         image = DockerImage(name='orambla/anella')
        self.cloud = CloudService(name='cloud_service2',
                                 summary = "summary 2",
                                 description = "description 2",
                                 link = "http://link2.com",
                                 provider = self.provider,
                                 keywords= [ "analysis" ],
                                 sectors= [ "cities" ],
#                                  images = [image,],
                                )
        self.cloud.save()

    def create_project(self):
        c_generic= ServiceContext(service=self.generic)
        c_generic.save()
        c_cloud =  ServiceContext(service=self.cloud)
        c_cloud.save()
        self.project = Project(name='project1', client=self.client, 
                          services=[ c_generic, c_cloud ]
#                           services = {
#                               service.name : ServiceContext(service=service),
#                               cloud.name : ServiceContext(service=cloud),
#                            }
                          )
        self.project.save()

class AnellaTestCase(unittest.TestCase, DocLoader):

    def setUp(self):
        utils.load_config('test-config.yaml', True)
        utils.reset_database()

    def tearDown(self):
        connection._connection_settings = {}
        connection._connections = {}
        connection._dbs = {}

