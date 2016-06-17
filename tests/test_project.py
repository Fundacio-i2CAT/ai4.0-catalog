# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError

from utils import AnellaTestCase
import anella.configuration as cfg

__all__ = ('ProjectTest', )


class ProjectTest(AnellaTestCase):

    def test_project_save(self):
        self.create_provider()
        self.create_client()
        self.create_ssh()
        self.create_scontext()
        self.create_project()


if __name__ == '__main__':
    unittest.main()

