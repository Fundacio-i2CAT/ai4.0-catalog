import sys
import datetime
import unittest
import uuid

from mongoengine import connect, connection

from anella import configuration as cfg
from anella.database import Database
from anella.utils import load_config, reset_database

from anella.model.user import User

__all__ = ('AnellaTestCase', )


class AnellaTestCase(unittest.TestCase):

    def setUp(self):
        load_config('test-config.yaml', True)
        reset_database()
        db = connect(db=cfg.database__database_name, 
                     host=cfg.database__host, port=cfg.database__port)

        user = User(cfg.admin__email, admin=True, staff=True)
        user.save()

    def tearDown(self):
        connection._connection_settings = {}
        connection._connections = {}
        connection._dbs = {}

