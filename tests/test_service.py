# -*- coding: utf-8 -*-

import sys
import datetime
import unittest
import uuid

from mongoengine import NotUniqueError

from anella.model.user import User
from anella.model.partner import Partner, Provider, Client, User, Contact, ANELLA_SECTORS
from anella.model.service import GenericService, CloudService, VMImage, DockerImage

from tests import AnellaTestCase, cfg

__all__ = ('ServiceTest', )


class ServiceTest(AnellaTestCase):

    def test_service_save(self):
        user = User(email='prov1@company1.com')
        user.save()
        provider = Provider(name='prov1', 
                            contact = Contact(email='prov1@company1.com'),
                            users=[user,],
                            sectors=[ sector[0] for sector in ANELLA_SECTORS],
                           )
        provider.save()

        image = DockerImage(name='orambla/anella')
        service = GenericService(name='service1',
                                 provider = provider,
                                 images = [image,],
                                )
        service.save()

#         cloud = CloudService(name='cloud_service1')
#         cloud.save()

if __name__ == '__main__':
    unittest.main()

