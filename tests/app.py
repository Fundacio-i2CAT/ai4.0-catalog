# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
from time import sleep

from mongoengine import NotUniqueError
from flask import json, jsonify

from utils import AnellaTestCase

from anella import utils
from anella import common
from anella import configuration as cfg
from anella import flask_app

__all__ = ('AppTestCase', )

sys.argv=sys.argv[:2]
app = flask_app.create_app(cfg_file='test-config.yaml', testing=True, debug=True)

class AppTestCase(AnellaTestCase):

    def setUp(self):
        utils.reset_database()
        self.app = app.test_client()

if __name__ == '__main__':
    unittest.main()
