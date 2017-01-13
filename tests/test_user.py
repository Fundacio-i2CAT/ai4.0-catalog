# -*- coding: utf-8 -*-

import unittest

from mongoengine import NotUniqueError
from utils import AnellaTestCase

from anella.common import *
from anella.model.user import User

__all__ = ('UserTest', )


class UserTest(AnellaTestCase):

    def test_user_save(self):
        user = User(email='pepe@i2cat.net', auth_id=23)
        user.save()
        self.assertIsNotNone(user.pk)

        with self.assertRaises(NotUniqueError):
            user = User(email='pepe@i2cat.net')
            user.save()

if __name__ == '__main__':
    unittest.main()

