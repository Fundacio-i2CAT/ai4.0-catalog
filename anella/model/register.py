from mongoengine import *
from base import Base
from anella.api.utils import respond_json, error_api
from anella.common import get_db, get_cfg
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from anella import configuration as _cfg


class Register(Document, Base):
    """
    """
    meta = {'allow_inheritance': True, 'collection': 'register'}

    # Collection fields
    email = StringField()
    name = StringField()
    surname = StringField()

    company = StringField()
    comp_position = StringField()
    legal = BooleanField()
    comp_address = StringField()
    comp_phone = StringField()
    password = StringField()
    client_role = BooleanField()
    provider_role = BooleanField()
    nif_cif = StringField()
    company = StringField()

    def set_email(self, email):
        self.email = email

    def set_name(self, name):
        self.name = name

    def set_surname(self, surname):
        self.surname = surname

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

    def set_nif_cif(self, identification):
        self.nif_cif = identification

    def set_company(self, company):
        self.company = company


def create_register(item):
    try:
        if exists_register(item) > 0:
            response = dict(status='409', msg="This register already exists.")
            return respond_json(response, status=409)
        register = set_register(item)
        register.save()
        send_email(item)
        response = dict(status='ok', id=unicode(register.pk), msg="Register created.")
        return respond_json(response, status=201)
    except Exception, e:
        response = dict(status='404', msg=e.message)
        return respond_json(response, status=404)


def set_register(item):
    register = Register()
    register.set_email(item.get('email'))
    register.set_name(item.get('name'))
    register.set_surname(item.get('surname'))
    register.set_company(item.pop('company'))
    register.set_comp_position(item.pop('comp_position'))
    register.set_legal(item.pop('legal'))
    register.set_com_address(item.pop('comp_address'))
    register.set_comp_phone(item.pop('comp_phone'))
    register.set_password(item.pop('password'))
    register.set_client_role(item.pop('client_role'))
    register.set_provider_role(item.pop('provider_role'))

    idn = item.pop('identification_number')
    register.set_nif_cif(idn['value'])
    return register


def exists_register(item):
    search_fields = {'email': item.get('email')}
    if item.get('identification_number')['isnif']:
        search_fields = {'email': item.get('email'), 'nif_cif': item.get('identification_number')['value']}
    return find_register_by_fields(search_fields)


def find_register_by_fields(search_fields):
    return get_db(_cfg.database__database_name)['register'].count(search_fields)


def send_email(item):
    toaddr = get_cfg('mail__to')
    fromaddr = get_cfg('mail__from')
    msg = MIMEMultipart()
    msg['Subject'] = get_cfg('mail__subject')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    body = get_cfg('mail__body') + ':\n\n Nom: ' + item.pop('name') + '\n\n Cognoms: ' \
           + item.pop('surname') + '\n\n Email: ' + item.pop('email')
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP(get_cfg('mail__smtp'), get_cfg('mail__port'))
    server.starttls()
    server.login(fromaddr, get_cfg('mail__pass'))
    server.sendmail(msg.get('From'), msg["To"], msg.as_string())
    server.quit()
    server.close()
