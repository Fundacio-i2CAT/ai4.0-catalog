# -*- coding: utf-8 -*-

from mongoengine import *
from base import Base

class User(Document, Base):
    meta = {'allow_inheritance': True, 'collection': 'users'}

    email = EmailField(required=True, unique=True)
    user_name = StringField(max_length=50, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    partner_id = ObjectIdField()

    admin = BooleanField(default=False)
    staff = BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not getattr(self, 'user_name', None):
             self.user_name = self.email.split('@')[0]

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

