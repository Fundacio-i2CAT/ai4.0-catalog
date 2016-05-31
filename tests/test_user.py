# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError
from utils import AnellaTestCase

import anella.configuration as cfg
from anella.model.user import User

__all__ = ('UserTest', )


class UserTest(AnellaTestCase):

    def test_user_save(self):
        with self.assertRaises(NotUniqueError):
            user = User(email=cfg.admin__email)
            user.save()

        with self.assertRaises(NotUniqueError):
            user = User(user_name=cfg.admin__user)
            user.save()

if __name__ == '__main__':
    unittest.main()

