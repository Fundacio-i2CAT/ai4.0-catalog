# -*- coding: utf-8 -*-

from mongoengine import *

class User(Document):
    email = EmailField(required=True, unique=True)
    user_name = StringField(max_length=50, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)

    admin = BooleanField(default=False)
    staff = BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not getattr(self, 'user_name', None):
             self.user_name = self.email.split('@')[0]

        super(User, self).save(self, *args, **kwargs)

    def is_provider(self):
        return True

    def is_client(self):
        return True

    def is_admin(self):
        return self.admin

