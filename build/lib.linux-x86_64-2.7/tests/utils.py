
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
                         admin=True, staff=True, phone_number="555 55 55 55", nif='5555555R' )
        self.admin.save()

    def create_user(self):
        self.user = User(email='user.last@i2cat.net', phone_number="666 66 66 66", nif='6666666R')
        self.user.save()

    def create_provider(self):
        # user = User(email='prov1@prov1.com')
        # user.save()
        contact = Contact( email='user.prov1@prov1.com' )
        self.provider = Provider(name='prov1', 
                            contact = contact,
                            # users=[user,],
                            nif='B77777777',
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        self.provider.save()

    def create_client(self):
        # user = User(email='client1@client1.com')
        # user.save()
        contact = Contact(email='user.client1@client1.com')
        self.client = Client(name='client1', 
                            contact = contact,
                            # users=[user,],
                            partner_type='research',
                            nif='B88888888',
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        self.client.save()

    def create_generic(self):
        from anella.model.service import AppService

#         image = DockerImage(name='orambla/anella')
        self.generic = AppService(name='service1',
                                 summary = "summary 1",
                                 description = "description 1",
                                 link = "http://link1.com",
                                 provider = self.provider,
                                 keywords= [ "storage" ],
                                 sectors= [ "industry" ],
                                 properties={'context_type':'ssh'}
#                                  images = [image,],
                                )
        self.generic.save()

    def create_cloud(self):
        from anella.model.service import ISService
#         image = DockerImage(name='orambla/anella')
        self.cloud = ISService(name='cloud_service2',
                                 summary = "summary 2",
                                 description = "description 2",
                                 link = "http://link2.com",
                                 provider = self.provider,
                                 keywords= [ "analysis" ],
                                 sectors= [ "cities" ],
                                 properties={'context_type':'openstack'}
#                                  images = [image,],
                                )
        self.cloud.save()


    def create_scontext(self):
        from anella.model.scontext import SContext

#         self.sc1 = SContext(name='scontext1', schema_file_name='schemas/schema-test.json' )
        context={
        "service_name" : "apache2.service",
        "host" : "87.236.219.21",
        "user_name" : "test",
        "password" : "test",
        "port" : 22,
#             'host': '',
#             'port': 22,
#             'user_name': 'oscar.rambla',
#             'password': 'oscar.rambla',
#             'service_name': 'apachectl',
        "openstack" : {
            "name_instance" : "test-openstack-1",
            "auth_url" : "http://87.236.219.10:5000/v3",
            "username" : "i2cat",
            "password" : "c5QWZTSv9gn0",
            "project_id" : "579eaa7245d04e778f0effd77565794c",
            "user_domain_name" : "i2cat",
            "flavor" : "VM.M1",
            "image" : "CentOS Cloud Base",
            "network" : "tenant-i2cat-demo"
            }
        }
     
        self.scontext = SContext(name='openstack',
                                 context_type='openstack',
                                 context=context,
                                )
        self.scontext.save()

#     def create_sc2(self):
# #         self.sc2 = SContext(name='scontext2', schema_file_name='schemas/schema-test.json' )
#         self.sc2 = SContext(name='scontext2' )
#         self.sc2.save()

    def create_scontext_ssh(self):
        from anella.model.scontext import SContext
        self.scontext_ssh = SContext(name='context_apache',
                                 context_type='ssh',
                                 context={
        "service_name" : "apache2.service",
        "host" : "84.88.34.24",
        "openstack" : {},
        "password" : "segmngr",
        "user_name" : "test",
        "port" : 22
    }
                                )
        self.scontext_ssh.save()

    def create_scontext1(self):
        from anella.model.scontext import SContext

#         self.sc1 = SContext(name='scontext1', schema_file_name='schemas/schema-test.json' )
        context={
#             'parameters':{
#                 'service_name': '${service_name}',
#                 'host': 'localhost',
#                 'port': 22,
#                 'user_name': 'oscar.rambla',
#                 'password': 'oscar.rambla'
#             },
#             'lifecycle_events': {
#                 'start': {
#                     'cmd': 'start ${service_name}'
#                  },
#                 'stop': {
#                     'cmd': 'stop ${service_name}'
#                  }
#             }
#         "openstack" : {
            "name_instance" : "test-openstack-1",
            "auth_url" : "http://87.236.219.10:5000/v3",
            "username" : "i2cat",
            "password" : "c5QWZTSv9gn0",
            "project_id" : "579eaa7245d04e778f0effd77565794c",
            "user_domain_name" : "i2cat",
            "flavor" : "VM.M1",
            "image" : "CentOS Cloud Base",
            "network" : "tenant-i2cat-demo"
#             }
        }
     
        self.scontext1 = SContext(name='cloud',
                                 context_type='cloud',
                                 context=context,
                                )
        self.scontext1.save()

    def create_apache_service(self):
        from anella.model.service import AppService

#         image = DockerImage(name='orambla/anella')
        properties={
            'service_name' : 'apache2',
            'context_type' : 'ssh',
        }
        self.apache = AppService(name='apache',
                                 summary = "summary apache",
                                 description = "description apache",
                                 link = "http://linkapache.com",
                                 provider = self.provider,
                                 keywords= [ "web", "server" ],
                                 sectors= [ "industry" ],
#                                  images = [image,],
                                 properties=properties
                                )
        self.apache.save()

    def create_apache1_service(self):
        from anella.model.service import AppService, ISService

#         image = DockerImage(name='orambla/anella')
        properties={
            'service_name' : 'apache2',
            'context_type' : 'ssh',
        }
        self.apache1 = AppService(name='apache1',
                                 summary = "summary apache1",
                                 description = "description apache1",
                                 link = "http://linkapache.com",
                                 provider = self.provider,
                                 keywords= [ "web", "server" ],
                                 sectors= [ "industry" ],
#                                  images = [image,],
                                 properties=properties
                                )
        self.apache1.save()


    def create_project(self):
        from anella.model.project import SProject, Project

        self.project = Project(name='project1', client=self.client,) 
#                           services=[ c_generic, c_cloud ]
#                           services = {
#                               service.name : SContext(service=service),
#                               cloud.name : SContext(service=cloud),
#                            }
        self.project.save()

        # context = self.scontext.resolve_parameters(self.apache.properties)
        context = self.scontext.context
        self.sproject= SProject(project=self.project, service=self.apache, 
                                context_type=self.scontext.context_type, context=context )
        self.sproject.save()
        self.project.services.append(self.sproject)
        self.project.save()

    def create_project1(self):
        from anella.model.project import SProject, Project

        self.project1 = Project(name='project2', client=self.client,) 
#                           services=[ c_generic, c_cloud ]
#                           services = {
#                               service.name : SContext(service=service),
#                               cloud.name : SContext(service=cloud),
#                            }
        self.project1.save()

        sproject= SProject(project=self.project1, service=self.generic, 
                                context_type=self.scontext.context_type, 
                                context= self.scontext.context
                          )
        sproject.save()
        self.project1.services.append(sproject)

        sproject= SProject(project=self.project1, service=self.cloud, 
                                context_type=self.scontext1.context_type, 
                                context= self.scontext1.context )
        sproject.save()
        self.project1.services.append(sproject)
        self.project1.save()

    def create_instance(self):
        from random import randint
        from anella.model.instance import Instance
        self.instance= Instance(sproject=self.sproject, 
                                instance_id=str(randint(1,9999)),
                                # context_type=self.scontext.context_type, 
                                # context=self.sproject.context 
                               )
        self.instance.save()


class AnellaTestCase(unittest.TestCase, DocLoader):

    def setUp(self):
        utils.load_config('test-config.yaml', True)
        reset_database()

    def tearDown(self):
        connection._connection_settings = {}
        connection._connections = {}
        connection._dbs = {}

