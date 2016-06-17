
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
# from anella.model.service import VMImage, DockerImage

def reset_database():
    common.reset_db()

class DocLoader(object):

    def create_admin(self):
        self.admin = User(email=cfg.admin__email, user_name=cfg.admin__user,
                         admin=True, staff=True)
        self.admin.save()

    def create_user(self):
        self.user = User(email='user.prov@prov1.com')
        self.user.save()

    def create_provider(self):
        # user = User(email='prov1@prov1.com')
        # user.save()
        contact = Contact( email='prov1@prov1.com' )
        self.provider = Provider(name='prov1', 
                            contact = contact,
                            # users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        self.provider.save()

    def create_client(self):
        # user = User(email='client1@client1.com')
        # user.save()
        contact = Contact(email='client1@client1.com')
        self.client = Client(name='client1', 
                            contact = contact,
                            # users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        self.client.save()

    def create_generic(self):
        from anella.model.service import GenericService, CloudService

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
        from anella.model.service import GenericService, CloudService
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

    def create_ssh(self):
        from anella.model.service import GenericService, CloudService
#         image = DockerImage(name='orambla/anella')
        self.ssh = GenericService(name='ssh',
                                 summary = "summary ssh",
                                 description = "description ssh",
                                 link = "http://linkssh.com",
                                 provider = self.provider,
                                 keywords= [ "ssh" ],
                                 sectors= [ "industry" ],
#                                  images = [image,],
                                )
        self.ssh.save()


    def create_scontext(self):
        from anella.model.scontext import SContext

#         self.sc1 = SContext(name='scontext1', schema_file_name='schemas/schema-test.json' )
        properties={
            'host': 'localhost',
            'port': 22,
            'user_name': 'oscar.rambla',
            'password': 'oscar.rambla',
            'service_name': 'apachectl',
        }
     
        self.scontext = SContext(name='context_ssh',
                                 context_type='ssh',
                                 properties=properties,
                                )
        self.scontext.save()

#     def create_sc2(self):
# #         self.sc2 = SContext(name='scontext2', schema_file_name='schemas/schema-test.json' )
#         self.sc2 = SContext(name='scontext2' )
#         self.sc2.save()

    def create_project(self):
        from anella.model.project import SProject, Project

        self.project = Project(name='project1', client=self.client,) 
#                           services=[ c_generic, c_cloud ]
#                           services = {
#                               service.name : SContext(service=service),
#                               cloud.name : SContext(service=cloud),
#                            }
        self.project.save()
        self.sproject= SProject(project=self.project, service=self.ssh, context=self.scontext)
        self.sproject.save()

class AnellaTestCase(unittest.TestCase, DocLoader):

    def setUp(self):
        utils.load_config('test-config.yaml', True)
        reset_database()

    def tearDown(self):
        connection._connection_settings = {}
        connection._connections = {}
        connection._dbs = {}

