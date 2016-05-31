import datetime
import unittest
import uuid

from mongoengine import NotUniqueError, Document

from utils import AnellaTestCase
import anella.configuration as cfg
from anella.model.base import Base

__all__ = ('BaseTest', )

class TBase(Document, Base):
    pass

class BaseTest(AnellaTestCase):

    def test_base_save(self):
        tbase = TBase()
        tbase.save()
        self.assertIsNotNone( tbase.created_at )
        self.assertIsNotNone( tbase.created_by )
        tbase.save()
        self.assertIsNotNone( tbase.updated_at )
        self.assertIsNotNone( tbase.updated_by )
        self.assertNotEqual( tbase.created_at, tbase.updated_at )

if __name__ == '__main__':
    unittest.main()

