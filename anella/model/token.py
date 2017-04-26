from mongoengine import Document
from anella.model.base import Base
from anella.common import get_db
import anella.configuration as cfg

class Token(Document, Base):
    def __init__(self, *args, **values):
        super(Token, self).__init__(*args, **values)

    def get(self):
        cursor = get_db(cfg.database__database_name).get_collection('token').find()
        return cursor.__getitem__(0)['token']