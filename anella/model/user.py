# -*- coding: utf-8 -*-

from mongoengine import *
from base import Base

IDIOMS = [
    (u'ca', u'Català'),
    (u'es', u'Español'),
    (u'en', u'English'),
]

class User(Document, Base):
    meta = {'allow_inheritance': True, 'collection': 'users'}

    email = EmailField(required=True, unique=True)
    user_name = StringField(max_length=50, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    phone_number = StringField(max_length=50)
    auth_id = StringField() # Id returned from Eurecat auth module

    idiom = StringField(choices=IDIOMS, default='ca')
    partner_id = ObjectIdField()

    admin = BooleanField(default=False)
    staff = BooleanField(default=False)


    def save(self, *args, **kwargs):
        user_name = getattr(self, 'user_name', None)
        first_name = getattr(self, 'first_name', None)
        last_name = getattr(self, 'last_name', None)
        if not user_name:
             self.user_name = self.email.split('@')[0]
             if '.' in self.user_name and not(first_name or last_name):
                 self.first_name,self.last_name=self.user_name.split('.')

        super(User, self).save(*args, **kwargs)

    def has_password(self, password):
        """ Should deviate comprobation to Auth module.
        """
        return password==self.user_name

    def set_password(self, password):
        pass

    def is_provider(self):
        return True

    def is_client(self):
        return True

    def is_admin(self):
        return self.admin

