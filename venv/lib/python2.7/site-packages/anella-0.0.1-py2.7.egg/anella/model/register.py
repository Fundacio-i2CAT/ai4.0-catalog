from mongoengine import *
from base import Base
from anella.api.utils import respond_json


class Register(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'register'}

    # Collection fields
    email = StringField()
    name = StringField()
    second_name = StringField()
    last_name = StringField()

    company = StringField()
    comp_position = StringField()
    legal = BooleanField()
    comp_address = StringField()
    comp_phone = StringField()
    password = StringField()
    client_role = BooleanField()
    provider_role = BooleanField()

    def set_email(self, email):
        self.email = email

    def set_name(self, name):
        self.name = name

    def set_second_name(self, second_name):
        self.second_name = second_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_company(self, company):
        self.company = company

    def set_comp_position(self, comp_position):
        self.comp_position = comp_position

    def set_legal(self, legal):
        self.legal = legal

    def set_com_address(self, comp_address):
        self.comp_address = comp_address

    def set_comp_phone(self, comp_phone):
        self.comp_phone = comp_phone

    def set_password(self, password):
        self.password = password

    def set_client_role(self, client_role):
        self.client_role = client_role

    def set_provider_role(self, provider_role):
        self.provider_role = provider_role


def create_register(item):
    try:
        register = set_register(item)
        register.save()
        response = dict(status='ok', id=unicode(register.pk), msg="Register created.")
        return respond_json(response, status=201)
    except Exception, e:
        response = dict(status='nok', msg=e.message)
        return respond_json(response, status=404)


def set_register(item):
    register = Register()
    register.set_email(item.pop('email'))
    register.set_name(item.pop('name'))
    register.set_second_name(item.pop('secondname'))
    register.set_last_name(item.pop('lastname'))
    register.set_company(item.pop('company'))
    register.set_comp_position(item.pop('comp_position'))
    register.set_legal(item.pop('legal'))
    register.set_com_address(item.pop('comp_address'))
    register.set_comp_phone(item.pop('comp_phone'))
    register.set_password(item.pop('password'))
    register.set_client_role(item.pop('client_role'))
    register.set_provider_role(item.pop('provider_role'))

    return register

