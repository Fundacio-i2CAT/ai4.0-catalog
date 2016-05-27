# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError
from tests import AnellaTestCase, cfg

from anella.model.user import User
from anella.model.partner import Partner, Provider, Client, User, Contact, ANELLA_SECTORS

__all__ = ('PartnerTest', )


class PartnerTest(AnellaTestCase):

    def test_partner_save(self):
        user = User(email='prov1@company1.com')
        user.save()
        provider = Provider(name='prov1', 
                            contact = Contact(email='prov1@company1.com'),
                            users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        provider.save()

#         try:
#             cloud = CloudService(name='cloud_service1')
#             cloud.save()
#         except NotUniqueError:
#             pass

if __name__ == '__main__':
    unittest.main()

