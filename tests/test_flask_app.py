# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from mongoengine import NotUniqueError

from utils import AnellaTestCase

from anella.model.user import User
from anella.model.partner import Partner, Provider, Client, User, Contact, ANELLA_SECTORS
from anella.model.service import GenericService, CloudService, VMImage, DockerImage

from anella import utils
from anella import common
from anella import configuration as cfg
from anella import flask_app as server

__all__ = ('ServerTest', )

class ServerTestCase(AnellaTestCase):

    def setUp(self):
        sys.argv=sys.argv[:2]
        app = server.main(cfg_file='test-config.yaml', testing=True, debug=True)
        utils.reset_database()
        self.app = app.test_client()

    def test_empty_db(self):
        rv = self.app.get('/api/services')
        self.assertIn( b'No services', rv.data)

    def test_server_services(self):
        self.create_admin()
        self.create_provider()
        self.create_generic()
        self.create_cloud()
        sleep(1)

        # rc = self.app.post(u'/api/services/'+unicode(self.generic.pk), data=generic.to_json())
        rc = self.app.get(u'/api/services')
        self.assertIn( b' list', rc.data)

    def test_server_service(self):
        self.create_admin()
        self.create_provider()
        self.create_generic()

        service_id = unicode(self.generic.pk)

        sleep(1)
        rv = self.app.get('/')
        sleep(1)
        rc = self.app.get(u'/api/services/'+service_id)
        self.assertIn( service_id, rc.data)

        rc = self.app.delete('/api/services/'+service_id)
        self.assertIn( 'deleted', rc.data)


if __name__ == '__main__':
    unittest.main()
