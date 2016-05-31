# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError

from utils import AnellaTestCase

__all__ = ('ServiceTest', )


class ServiceTest(AnellaTestCase):

    def test_service_save(self):
        self.create_provider()
        self.create_generic()
        self.create_cloud()

if __name__ == '__main__':
    unittest.main()

