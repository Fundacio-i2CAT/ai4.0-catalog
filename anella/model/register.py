from anella.api.utils import respond_json
from anella.common import get_db, get_cfg
import smtplib
from anella.api.service_manager_mailer import ServiceManagerMailer
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from requests import Session
from anella.api.utils import create_response

import json

class RegisterEurecat(object):
    def __init__(self):
        self.name = None
        self.surname = None
        self.email = None
        self.password = None
        self.identifier = None
        self.phone = None
        self.company = None
        self.address = None
        self.postalCode = None
        self.jobPosition = None
        self.description = None
        self.country = None
        self.legal = False
        self.clientRole = False
        self.providerRole = False
        self.activated = False

class Register(object):
    def __init__(self):
        self.root_path='https://%s:%s/1.0/LmpApiI2cat/people' % (get_cfg('auth__host'), get_cfg('auth__port'))
        self.entity_association_path = 'https://%s:%s/1.0/LmpApiI2cat/personEntityRelationships' % (get_cfg('auth__host'), get_cfg('auth__port'))
        self.default_entity_path = 'https://%s:%s/1.0/LmpApiI2cat/entities/4' % (get_cfg('auth__host'), get_cfg('auth__port'))
        self.session = Session()
        with open(get_cfg('auth__oauth')) as fhandle:
            self.authorization = json.load(fhandle)
        self.session.headers.update(self.authorization['headers'])
        # Waiting for Eurecat's certificate ...
        #    meanwhile verification disabled
        self.session.verify = False
        self.user = RegisterEurecat()

    def create(self, data):
        self.create_dict(data)
        resp = self.session.post(self.root_path, json=self.user.__dict__)
        # ASOCIAMOS CON ENTIDAD DEFAULT ID=4 (PROVISIONAL)
        if not resp.status_code in (200, 201):
            return create_response(resp.status_code, resp.text)
        resp_data = json.loads(resp.text)
        user_id = resp_data['id']
        entity_association = {
            "state": "REQUESTED_FROM_USER",
            "organization": self.default_entity_path,
            "person": "{0}/{1}".format(self.root_path, user_id)
        }
        resp_association = self.session.post(self.entity_association_path,
                                             json=entity_association)
        if resp_association.status_code in (200, 201):
            smm = ServiceManagerMailer()
            smm.notify(self.user.email)
        return create_response(resp.status_code, resp.text)

    def create_dict(self, data):
        self.user.name = data.get('name')
        self.user.surname = data.get('surname')
        self.user.email = data.get('email')
        self.user.password = data.get('password')
        self.user.identifier = data.get('identification_number')['value']
        self.user.phone = data.get('comp_phone')
        self.user.company = data.get('company')
        self.user.address = data.get('comp_address')
        self.user.jobPosition = data.get('comp_position')
        self.user.legal = data.get('legal')
        self.user.clientRole = data.get('client_role')
        self.user.providerRole = data.get('provider_role')


    def send_email(self):
        toaddr = get_cfg('mail__to')
        fromaddr = get_cfg('mail__from')
        msg = MIMEMultipart()
        msg['Subject'] = get_cfg('mail__subject')
        msg['From'] = fromaddr
        msg['To'] = toaddr
        body = get_cfg('mail__body') + ':\n\n Nom: ' + self.user.name + '\n\n Cognoms: ' \
               + self.user.surname + '\n\n Email: ' + self.user.email
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(get_cfg('mail__smtp'), get_cfg('mail__port'))
        server.starttls()
        server.login(fromaddr, get_cfg('mail__pass'))
        server.sendmail(msg.get('From'), msg["To"], msg.as_string())
        server.quit()
        server.close()
