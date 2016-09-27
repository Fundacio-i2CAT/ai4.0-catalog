# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError

from utils import AnellaTestCase

import anella.configuration as cfg

__all__ = ('PartnerTest', )


class PartnerTest(AnellaTestCase):

    def test_prov_save(self):
        self.create_provider()

    def test_client_save(self):
        self.create_client()

if __name__ == '__main__':
    unittest.main()

