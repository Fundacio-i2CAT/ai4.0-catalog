# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError
from tests import AnellaTestCase, cfg
from anella.model.user import User

__all__ = ('UserTest', )


class UserTest(AnellaTestCase):

    def test_user_save(self):
        with self.assertRaises(NotUniqueError):
            user = User(cfg.admin__email)
            user.save()

if __name__ == '__main__':
    unittest.main()

