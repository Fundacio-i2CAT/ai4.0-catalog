# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid
import json

from mongoengine import NotUniqueError

from utils import AnellaTestCase
import anella.configuration as cfg

from anella.template import is_template

__all__ = ('SContextTest', )


class SContextTest(AnellaTestCase):

    def test_scontext_save(self):
        self.create_provider()
        self.create_client()
        self.create_scontext()

    def test_resolve(self):
        self.create_provider()
        self.create_client()
        self.create_scontext()
        self.create_apache_service()
        context = self.scontext.resolve_parameters(self.apache.properties)
        self.assertEqual(is_template(json.dumps(context)), False)


if __name__ == '__main__':
    unittest.main()

