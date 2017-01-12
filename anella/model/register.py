from anella.api.utils import respond_json
from anella.common import get_db, get_cfg
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from anella import configuration as _cfg
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

    def create(self, data):
        user = self.create_dict(data)
        resp = self.session.post(self.root_path, json=user.__dict__)
        return create_response(resp.status_code, resp.text)

    def create_dict(self, data):
        user = RegisterEurecat()
        user.name = data.get('name')
        user.surname = data.get('surname')
        user.email = data.get('email')
        user.password = data.get('password')
        user.identifier = data.get('identification_number')['value']
        user.phone = data.get('comp_phone')
        user.company = data.get('company')
        user.address = data.get('comp_address')
        user.jobPosition = data.get('comp_position')
        user.legal = data.get('legal')
        user.clientRole = data.get('client_role')
        user.providerRole = data.get('provider_role')
        return user
    """
    """
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
    register.set_comp_position(item.pop('comp_position')) #company
    register.set_legal(item.pop('legal'))
    register.set_com_address(item.pop('comp_address')) #address
    register.set_comp_phone(item.pop('comp_phone')) #phone
    register.set_password(item.pop('password'))
    register.set_client_role(item.pop('client_role')) #clientRole
    register.set_provider_role(item.pop('provider_role')) #providerRole

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
