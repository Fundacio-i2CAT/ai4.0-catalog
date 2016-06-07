# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError
from utils import AnellaTestCase

from anella.common import *
from anella.model.user import User

__all__ = ('UserTest', )


class UserTest(AnellaTestCase):

    def test_user_save(self):
        user = User(email='pepe@i2cat.net')
        user.save()
        self.assertIsNotNone(user.pk)

        with self.assertRaises(NotUniqueError):
            user = User(email='pepe@i2cat.net')
            user.save()

if __name__ == '__main__':
    unittest.main()

