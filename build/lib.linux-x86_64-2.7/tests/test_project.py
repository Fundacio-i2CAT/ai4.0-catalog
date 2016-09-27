# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid
from time import sleep
from bson import ObjectId

from mongoengine import NotUniqueError

from utils import AnellaTestCase
import anella.configuration as cfg

from anella.model.project import Project, SProject

__all__ = ('ProjectTest', )


class ProjectTest(AnellaTestCase):

    def create_all_project(self):
        self.create_admin()
        self.create_client()
        self.create_provider()
        self.create_scontext()
        self.create_scontext1()
        self.create_apache_service()
        self.create_project()
        sleep(1)

    def test_project_save(self):
        self.create_provider()
        self.create_client()
        self.create_scontext()
        self.create_apache_service()
        self.create_project()
#         import pdb;pdb.set_trace()
        sleep(1)

        project = Project.objects.get(id=ObjectId(self.project.pk))
        self.assertEqual(self.project,project)

        for sp in self.project.services:
            sp1 = SProject.objects.get(id=ObjectId(sp.pk))
            self.assertEqual(sp,sp1)


    def test_project1_save(self):
        self.create_provider()
        self.create_client()
        self.create_scontext()
        self.create_scontext1()
        self.create_generic()
        self.create_cloud()
        self.create_project1()

#         import pdb;pdb.set_trace()
        sleep(1)

        project1 = Project.objects.get(id=ObjectId(self.project1.pk))
        self.assertEqual(self.project1,project1)

        for sp in self.project1.services:
            sp1 = SProject.objects.get(id=ObjectId(sp.pk))
            self.assertEqual(sp,sp1)


if __name__ == '__main__':
    unittest.main()

