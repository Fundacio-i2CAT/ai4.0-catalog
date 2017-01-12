from anella.api.utils import respond_json
from anella.common import get_db, get_cfg
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from requests import Session
from anella.api.utils import create_response


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
        self.root_path = 'http://%s:%s/LmpApiI2cat/people' % (get_cfg('auth__host'), get_cfg('auth__port'))
        self.session = Session()
        self.user = RegisterEurecat()

    def create(self, data):
        self.create_dict(data)
        resp = self.session.post(self.root_path, json=self.user.__dict__)
        if resp.status_code in (200, 201):
            self.send_email()
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
