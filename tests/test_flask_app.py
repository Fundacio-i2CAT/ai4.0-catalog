# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from mongoengine import NotUniqueError

from anella.model.user import User
from anella.model.partner import Partner, Provider, Client, User, Contact, ANELLA_SECTORS
from anella.model.service import GenericService, CloudService, VMImage, DockerImage

from anella import utils
from anella import common
from anella import configuration as cfg
from anella import flask_app as server

__all__ = ('ServerTest', )

class ServerTestCase(unittest.TestCase):

    def setUp(self):
        sys.argv=sys.argv[:2]
        app = server.main(cfg_file='test-config.yaml', testing=True, debug=True)
        utils.reset_database()
        self.app = app.test_client()

    def test_empty_db(self):
        rv = self.app.get('/api/services')
        assert b'No services' in rv.data


    def test_server_services(self):
        user = User(email='prov2@company1.com')
        user.save()
        provider = Provider(name='prov2', 
                            contact = Contact(email='prov2@company1.com'),
                            users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        provider.save()

        image = DockerImage(name='orambla/anella')
        service = GenericService(name='service1',
                                 provider = provider,
                                 images = [image,],
                                )
        service.save()
        sleep(1)

        service = GenericService(name='service2',
                                 provider = provider,
                                 images = [image,],
                                )
        service.save()
        sleep(1)

        rc = self.app.post(u'/api/services/'+unicode(service.pk), data=service.to_json())
        assert b'services list' in rc.data

#         cloud = CloudService(name='cloud_service2',
#                                  provider = provider,
#                                  images = [image,],
#                                 )
#         cloud.save()

        # import pdb;pdb.set_trace()
        sleep(1)
        rv = self.app.get('/')
        sleep(1)
        rc = self.app.get('/api/services')
        assert b'services list' in rc.data

    def test_server_service(self):
        user = User(email='prov2@company1.com')
        user.save()
        provider = Provider(name='prov2', 
                            contact = Contact(email='prov2@company1.com'),
                            users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        provider.save()

        image = DockerImage(name='orambla/anella')
        service = GenericService(name='service1',
                                 provider = provider,
                                 images = [image,],
                                )
        service.save()
        service_id = unicode(service.pk)

#         cloud = CloudService(name='cloud_service2',
#                                  provider = provider,
#                                  images = [image,],
#                                 )
#         cloud.save()

        # import pdb;pdb.set_trace()
        sleep(1)
        rv = self.app.get('/')
        sleep(1)
        rc = self.app.get(u'/api/services/'+service_id)
        assert service_id in rc.data

        rc = self.app.delete('/api/services/'+service_id)
        assert 'deleted' in rc.data


if __name__ == '__main__':
    unittest.main()
