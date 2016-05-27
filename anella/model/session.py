# -*- coding: utf-8 -*-

from user import User

class Session(Document):
    user = ReferenceField(User)
    created_at = DateTimeField(default=datetime.now)
    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 3600}
        ]
    }

