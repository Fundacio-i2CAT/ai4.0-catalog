# -*- coding: utf-8 -*-

from bson import ObjectId
import os
from anella.common import *
from anella.model.project import Project, SProject, SAVED, DISABLED, CONFIRMED, STATES, STATUS, Client, \
    ServiceDescription, Provider
from anella.model.instance import Instance
from anella.model.service import VMImage

from anella.orch import Orchestrator
from anella.api.utils import regex_name, get_int, Resource, ColRes, ItemRes, \
    respond_json, error_api, item_to_json, create_message_error, \
    update_status_project, find_one_in_collection, count_collection
from anella import configuration as _cfg
import json
from anella.model.project import STATUS
from datetime import datetime
from mongoengine import NotUniqueError
from anella.security.authorize import get_exists_user, get_authorize_projects

def services_to_json(sprojects):
    sitems = []
    for service_id in sprojects:
        sproject = get_db(_cfg.database__database_name)['sprojects'].find_one({'_id': service_id})
        sitem = item_to_json(sproject, ['_id', 'context_type', 'status', 'provider', 'created_at'])
        service = get_db(_cfg.database__database_name)['services'].find_one({'_id': sproject['service']})
        provider = get_db(_cfg.database__database_name)['users'].find_one({'_id': service['provider']})

        sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
        # sitem['service'] = item_to_json(service, ['_id', 'name'])
        sitem['service'] = item_to_json(service, ['_id', 'name'])
        sitems.append(sitem)

    return sitems


def sprojects_to_json(sprojects):
    # import pdb;pdb.set_trace()
    sitems = []
    for sproject in sprojects:
        sitem = sproject_to_json(sproject)
        sitems.append(sitem)

    return sitems


def sproject_to_json(sproject, context=False):
    project = get_db(_cfg.database__database_name)['projects'].find_one({'_id': sproject['project']})
    sitem = item_to_json(sproject, ['_id', 'status', 'created_at'])
    service = get_db(_cfg.database__database_name)['services'].find_one({'_id': sproject['service']})
    provider = get_db(_cfg.database__database_name)['users'].find_one({'_id': service['provider']})
    client = get_db(_cfg.database__database_name)['users'].find_one({'_id': project['client']})

    sitem['project'] = item_to_json(project, ['_id', 'name'])
    sitem['client'] = item_to_json(client, ['_id', 'user_name'])
    sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
    # sitem['service'] = item_to_json(service, ['_id', 'name'])
    sitem['service'] = item_to_json(service, ['_id', 'name'])

    if context:
        sitem.update(item_to_json(sproject, ['context_type', 'context']))

    return sitem


def get_service(id_service):
    return get_db(_cfg.database__database_name)['services'].find_one({'_id': id_service})


def get_service_by_objectid(id_service):
    return get_db(_cfg.database__database_name)['services'].find_one({'_id': ObjectId(id_service)})


class ProjectStatesRes(Resource):
    @get_exists_user()
    def get(self):
        return [dict(status=st[0], name=st[1]) for st in STATUS]


class ProjectsRes(ColRes):
    collection = 'projects'
    _cls = Project
    name = 'Projects'
    fields = '_id,name,summary,client,status,services,created_at,updated_at,runtime_params'.split(',')
    filter_fields = 'name,status'.split(',')

    def _item_to_json(self, item):
        services = item.get('services')
        project = self._find_obj(item['_id'])
        item['status'] = project.get_status()
        item['services'] = services_to_json(services)
        return item_to_json(item, self.fields)

    @get_exists_user()
    def get(self):
        return ColRes.get(self)

    def post(self):
        item = get_json()
        return create_project(item)


class ProjectRes(ItemRes):
    collection = 'projects'
    _cls = Project
    name = 'Project'
    fields = '_id,name,summary,description,client,services,status,created_at,created_by,updated_at,updated_by'.split(
        ',')

    def _item_to_json(self, item):
        project = self._find_obj(item['_id'])
        item['status'] = project.get_status()
        services = item.get('services')
        item['services'] = services_to_json(services)
        return item_to_json(item, self.fields)

    @get_exists_user()
    @get_authorize_projects(None)
    def get(self, id):
        return super(ProjectRes, self).get(id)

    def put(self, id):
        """ Modifies the project when not confirmed.
            Use Project/state othercase
        """
        # import pdb;pdb.set_trace()
        project = self._find_obj(id)
        if not project:
            return error_api(msg='Error: wrong project id in request.', status=404)
        status = project.get_status()
        if status >= CONFIRMED:
            return error_api(msg='Error: project is confirmed yet.', status=400)

        item = get_json()
        return update_project(project, item)

    def delete(self, id):
        project = self._find_obj(id)
        if not project:
            return error_api(msg='Error: wrong project id in request.', status=404)
        status = project.get_status()
        for sproject in project.services:
            spres = SProjectRes()
            orch = Orchestrator(debug=False)
            item = spres._find_item(unicode(sproject.pk))
            instance = find_instance(unicode(item['_id']))
            if instance:
                orch.instance_delete(instance['instance_id'])
        return delete_project(project)

class ProjectStateRes(ProjectRes):
    def __init__(self):
        self.orch = Orchestrator(debug=False)
        self.spres = SProjectRes()
        self.consumer_params = None

    def _set_state(self, services, state):
        # Services are items (not obj)
        # import pdb;pdb.set_trace()
        for sproject in services:
            item = self.spres._find_item(unicode(sproject.pk))
            # Save consumer params in SProjects
            sproject.consumer_params = dict(consumer_params=self.consumer_params)
            sproject.save()
            instance = find_instance(unicode(item['_id']))
            if instance:
                if state == 'DISABLED':
                    ok = self.orch.instance_delete(instance['instance_id'])
                    if not ok:
                        return "Error instance '%s' delete." % instance['instance_id']
                    else:
                        sproject.instance_id = None
                        sproject.status = DISABLED
                        sproject.save()

                else:
                    response = self.orch.instance_set_state(instance['instance_id'], state)
                    code = None
                    if 'state' in response['response']:
                        code = get_status(response['response']['state'])
                        update_status_project(sproject.id, code)
                    if response['status_code'] not in (200, 201):
                        error_code = 'ORQUESTRATOR_STATE'
                        if 'code' in response['response']:
                            error_code = response['response']['code']
                        return create_message_error(response['status_code'],
                                                    error_code, code)

            else:
                # context para el orquestrador
                service = get_service(item['service'])
                context = service['context']
                # name_image = context['name_image']
                # Primero miramos si está la imagen cacheada en el orquestrador
                if (context['vm_image_format'] == 'openstack_id') or (self.exists_image(context)):
                    if context['vm_image_format'] == 'openstack_id':
                        context['vm_image'] = context['name_image']
                    else:
                        context['vm_image'] = _cfg.repository__ip + context['name_image']
                else:
                    # Si no lo está. Guardamos la imagen en local
                    context['vm_image'] = save_image_to_local(context['vm_image'], context['name_image'])
                # guardada la imagen. Seguimos
                context['consumer_params'] = self.consumer_params
                context = dict(context=context)
                resp = self.orch.instance_create(context)
                if resp.status_code in (200, 201):
                    data = json.loads(resp.text)
                    instance_id = data['service_instance_id']
                    instance = Instance(sproject=sproject, instance_id=instance_id)
                    instance.save()
                    # delete local image
                    # path_file = "{0}{1}".format(_cfg.repository__path, name_image)
                    # os.remove(path_file)
                else:
                    resp_text = ''
                    json_load = json.loads(resp.text)
                    if 'code' in json_load:
                        resp_text = json_load['code']
                    return create_message_error(resp.status_code, resp_text, '')

        error = self._get_state(services)
        if error['status_code'] not in (200, 201):
            return create_message_error(self.orch.req.status_code,
                                        json.loads(self.orch.req.text)['code'], '')

    def exists_image(self, service):
        context = dict(pop_id=1)
        if 'pop_id' in service:
            context['pop_id'] = service['pop_id']
        context['vm_image'] = _cfg.repository__ip + service['name_image']
        resp = self.orch.exists(context)
        exists = False
        if resp.status_code in (200, 201):
            exists = True
        return exists

    def _get_state(self, services):
        # Services are items (not obj)
        # import pdb;pdb.set_trace()
        project_status = None
        data = None
        for sproject in services:
            service_id = unicode(sproject.pk)
            item = self.spres._find_item(unicode(service_id))
            instance = find_instance(unicode(item['_id']))
            if sproject.status == DISABLED:
                project_status = DISABLED
                break
            if instance:
                data = self.orch.instance_get_state(instance['instance_id'])
                if self.orch.req.status_code not in (200, 201):
                    code = None
                    response = json.loads(self.orch.req.text)
                    if 'state' in response:
                        code = get_status(response['state'])
                        update_status_project(sproject.pk, code)
                        error_code = 'ORQUESTRATOR_STATE'
                    if 'code' in response:
                        error_code = response['code']
                    return create_message_error(self.orch.req.status_code,
                                                error_code, code)
                state = data['state']
                if state:
                    status = STATES.index(state)
                    # 20160719 Cache status in db
                    sproject.status = status
                    sproject.runtime_params = dict(runtime_params=data['runtime_params'])
                    sproject.save()
                    if project_status is None or status < project_status:
                        project_status = status
                    continue
                else:
                    code = get_status('FAILED')
                    update_status_project(sproject.pk, code)
                    return create_message_error(404, _cfg.errors__orchestrator_state, code)
                    # some error
                    # break

        if (project_status is None) or (data is None):
            return create_message_error(404, _cfg.errors__orchestrator_state, '')
        else:
            return dict(status_code=self.orch.req.status_code, status=project_status,
                        state=STATES[project_status], runtime_params=data['runtime_params'])

    @get_exists_user()
    @get_authorize_projects(None)
    def get(self, id):
        # import pdb;pdb.set_trace()
        self.project = self._find_obj(id)
        if not self.project:
            return error_api(msg='Error: wrong project id in request.', status=404)
        status = self.project.get_status()
        if status < CONFIRMED:
            response = dict(state=STATES[status], status=status, project_id=id)
            return respond_json(response, status=200)

        resp = self._get_state(self.project.services)
        if resp['status_code'] not in (200, 201):
            return respond_json(resp, status=resp['status_code'])
        if resp['state']:
            return respond_json({"status": resp["status"], "state": resp['state'], "project_id": id}, status=200)
        else:
            response = dict(state='CONFIRMED', status=3, project_id=id)
            return respond_json(response, status=200)

    def put(self, id):
        # import pdb;pdb.set_trace()
        self.project = self._find_obj(id)
        if not self.project:
            return error_api(msg='Error: wrong project id in request.', status=404)
        status = self.project.get_status()
        if status < CONFIRMED:
            return error_api(msg='Error: project is not confirmed yet.', status=400)

        data = get_json()
        status = data.get('status')
        if status not in range(len(STATES)):
            return error_api(msg='Error: wrong status in request.', status=400)
        state = STATES[status]
        if state not in STATES:
            return error_api(msg='Error: wrong status in request.', status=400)
        # In any case ensure instances exist
        self.consumer_params = data.get('consumer_params')
        error = self._set_state(self.project.services, state)

        if error:
            return respond_json(error, status=error['status_code'])
        else:
            response = dict(status='ok', msg="Project state set to '%s'" % state)
            return respond_json(response, status=200)


class ProjectUpdateStateRes(ProjectRes):
    def __init__(self):
        self.orch = Orchestrator(debug=False)
        self.spres = SProjectRes()

    def put(self, id):
        # import pdb;pdb.set_trace()
        self.project = self._find_obj(id)
        if not self.project:
            return error_api(msg='Error: wrong project id in request.', status=404)

        data = get_json()
        status = data.get('status')
        if status not in range(len(STATES)):
            return error_api(msg='Error: wrong status in request.', status=400)
        state = STATES[status]
        if state not in STATES:
            return error_api(msg='Error: wrong status in request.', status=400)
        # In any case ensure instances exist
        error = self._update_state(self.project.services, state)

        if error:
            return respond_json(error, status=error['status_code'])
        else:
            response = dict(status='ok', msg="Project state set to '%s'" % state)
            return respond_json(response, status=200)

    def _update_state(self, services, state):
        # Services are items (not obj)
        # import pdb;pdb.set_trace()
        code = get_status(state)
        for sproject in services:
            item = self.spres._find_item(unicode(sproject.pk))
            instance = find_instance(unicode(item['_id']))
            if instance:
                if state == 'DISABLED':
                    ok = self.orch.instance_delete(instance['instance_id'])
                    if not ok:
                        return "Error instance '%s' delete." % instance['instance_id']
                    else:
                        sproject.instance_id = None
                        sproject.status = DISABLED
                        sproject.save()

                else:
                    response = self.orch.instance_set_state(instance['instance_id'], state)
                    code = None
                    if 'state' in response['response']:
                        code = get_status(response['response']['state'])
                        update_status_project(sproject.id, code)
                    if response['status_code'] not in (200, 201):
                        error_code = 'ORQUESTRATOR_STATE'
                        if 'code' in response['response']:
                            error_code = response['response']['code']
                        return create_message_error(response['status_code'],
                                                    error_code, code)
            elif code in (1, 3, 8):
                update_status_project(sproject.id, code)


class ClientProjectsRes(ProjectsRes):

    @get_exists_user()
    @get_authorize_projects('User.Client', False, 'client', True)
    def get(self, id):
        self.client_id = id
        return super(ClientProjectsRes, self).get()

    def _get_items(self, skip=0, limit=1000):
        values = get_args().copy()  # args are inmutable
        # status = int(values and values.pop('status', 0)) or None
        filter = self._filter_from_inputs(values)
        filter['client'] = ObjectId(self.client_id)
        cursor = get_db(_cfg.database__database_name)['projects'].find(filter, skip=skip, limit=limit)
        items = []
        for item in cursor:
            project = self._find_obj(item['_id'])
            status = project.get_status()
            if status == DISABLED:
                continue
            items.append(item)
        return items

    def _filter_from_inputs(self, values):
        filter = super(ClientProjectsRes, self)._filter_from_inputs(values)
        filter['client'] = ObjectId(self.client_id)
        return filter

    def _item_to_json(self, item):
        services = item.get('services')
        project = self._find_obj(item['_id'])
        sproject = get_db(_cfg.database__database_name)['sprojects'].find_one({'project': ObjectId(item['_id'])})
        item['status'] = project.get_status()
        item['services'] = services_to_json(services)
        if 'runtime_params' in sproject['runtime_params']:
            item['runtime_params'] = sproject['runtime_params']['runtime_params']
        else:
            item['runtime_params'] = sproject['runtime_params']
        return item_to_json(item, self.fields)


class SessionProjectRes(ProjectRes):
    collection = 'projects'
    _cls = Project
    name = 'Project'
    fields = '_id,name,summary,description,client,status,created_at,created_by,updated_at,updated_by'.split(',')

    def post(self):
        if get_session() and get_session().get('user'):
            user = User.objects.get(id=get_session().get('user'))
        else:
            return error_api("Not signed in.", status=400)

        item = get_json()
        item['client'] = user.partner_id
        return create_project(item)


class ProjectServicesRes(ColRes):
    collection = 'sprojects'
    _cls = SProject
    name = 'Service Contract'
    fields = '_id,service,status,created_at,updated_at'.split(',')

    #     filter_fields = 'name'.split(',')

    def post(self, id):
        try:
            project = Project.objects.get(id=ObjectId(id))
            obj = self._obj_from_json(get_json())
            obj.project = project
            valid_error = self._validate(obj)
            if valid_error:
                response = dict(status='fail', msg='%s: %s' % (self.name, valid_error))
                return respond_json(response, status=400)

            obj.save()
            response = dict(status='ok', msg='%s updated' % self.name)
            return respond_json(response, status=200)

        except Exception, e:
            return error_api(msg=str(e))

    def get(self, id):
        project = get_db(_cfg.database__database_name)['projects'].find_one({'_id': ObjectId(id)})
        result = services_to_json(project['services'])
        response = dict(status='ok', result=result)
        return respond_json(response, status=200)


class SProjectsRes(ColRes):
    collection = 'sprojects'
    _cls = SProject
    name = 'SProjects'
    fields = '_id,project,service,context,created_at'.split(',')

    def item_from_json(self, data):
        service_cls = get_service_cls(data.get('service_type'))
        if service_cls:
            self._cls = service_cls
        item = ColRes.item_from_json(self, data)
        item['_cls'] = service_cls._class_name
        # obj = service_cls.from_json(item)
        return item


class SProjectRes(ItemRes):
    collection = 'sprojects'
    _cls = SProject
    name = 'SProject'
    fields = 'project,service,context_type,context,created_at'.split(',')

    def _item_to_json(self, item):
        return sproject_to_json(item)

    def put(self, id):
        # import pdb;pdb.set_trace()
        self.sproject = self._find_obj(id)
        if not self.sproject:
            return error_api(msg='Error: wrong service project id in request.', status=404)
        data = get_json()
        status = data.get('status')
        if status not in [CONFIRMED, DISABLED]:  # Only support confirm by now. not in range(len(STATES)):
            return error_api(msg='Error: wrong status in request.', status=400)

        if status == CONFIRMED and self.sproject.status in range(CONFIRMED, DISABLED):
            return error_api(msg='Error: service project is already confirmed yet.', status=400)

        #         if status==DISABLED and self.sproject.status < CONFIRMED, DISABLED):
        #             return error_api( msg='Error: service project is already confirmed yet.', status=400 )

        state = STATES[status]
        self.sproject.status = status
        self.sproject.save()
        response = dict(status='ok', msg="Service project state set to %s" % state)
        return respond_json(response, status=200)


class SProjectStatusRes(SProjectRes):
    collection = 'sprojects'
    _cls = SProject
    name = 'SProject'
    fields = 'project,service,context_type,context,created_at'.split(',')

    @get_exists_user()
    @get_authorize_projects('User.Provider', is_same_user=True)
    def get(self, id):
        item = []
        limit = get_int(get_arg('limit'))
        skip = get_int(get_arg('skip'))
        _filter = self.get_status(id)
        print _filter
        result = super(SProjectStatusRes, self)._get_items(skip * limit, limit, _filter)
        for sproject in result:
            sitems = []
            sitem = {}
            project = find_one_in_collection('projects', {"services": {"$in": [ObjectId(sproject['_id'])]}})
            data = item_to_json(project, ['_id', 'name', 'summary', 'description', 'client', 'created_at'])
            data['sproject'] = str(sproject['_id'])
            data['status'] = sproject['status']
            service = find_one_in_collection('services', {'_id': sproject['service']})
            provider = find_one_in_collection('users', {'_id': service['provider']})
            client = find_one_in_collection('users', {"_id": ObjectId(project['client'])})
            sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
            sitem['service'] = item_to_json(service, ['_id', 'name'])
            data['client'] = item_to_json(client, ['_id', 'user_name'])
            data['provider'] = str(sproject['provider'])
            sitems.append(sitem)
            data['services'] = sitems
            item.append(data)
        response = dict(count=count_collection(self.collection, _filter), skip=skip, limit=limit,
                        result=item)
        return dict(response=response, status=200)

    def get_status(self, id):
        if get_arg('status') is None:
            return {'provider': ObjectId(id)}
        else:
            lst = get_arg('status').split(',')
            nums = []
            for x in lst:
                nums.append(int(x))
            return {'provider': ObjectId(id),
                    'status': {'$in': nums}}


class ProviderSProjectsRes(SProjectsRes):
    filter_fields = 'provider,status'.split(',')

    @get_exists_user()
    @get_authorize_projects('User.Provider', False, 'provider', True)
    def get(self, id):
        # import pdb;pdb.set_trace()
        self.provider_id = id
        return super(ProviderSProjectsRes, self).get()

    def _filter_from_inputs(self, values):
        # import pdb;pdb.set_trace()
        filter = super(ProviderSProjectsRes, self)._filter_from_inputs(values)
        filter['provider'] = ObjectId(self.provider_id)
        return filter

    def _get_items(self, skip=0, limit=1000):
        # import pdb;pdb.set_trace()
        values = get_args().copy()  # args are inmutable
        # status = int(values and values.pop('status', 0)) or None
        filter = self._filter_from_inputs(values)
        filter['provider'] = ObjectId(self.provider_id)
        cursor = get_db(_cfg.database__database_name)['sprojects'].find(filter, skip=skip, limit=limit).sort('created_at', -1)
        return [item for item in cursor]

    def _items_to_json(self, items):
        return sprojects_to_json(items)


class ProjectOrchCallbackRes(ProjectsRes):
    def post(self):
        instance_info = get_json()
        if 'image_path' in instance_info:
            try:
                instance = get_db(_cfg.database__database_name)['instances'].find_one({'instance_id': instance_info['service_instance_id']})
                sproject = get_db(_cfg.database__database_name)['sprojects'].find_one({'_id': ObjectId(instance['sproject'])})
                service = get_db(_cfg.database__database_name)['services'].find_one({'_id': ObjectId(sproject['service'])})
                image_path = '{0}.img'.format(str(service['context']['vm_image']))
                file_to_remove = '{0}{1}'.format(_cfg.repository__path,
                                                  image_path)
                os.remove(file_to_remove)
            except:
                respond_json({'message': 'Error removing {0}'.format(file_to_remove)}, status=500)
        return respond_json(instance_info, status=200)


def delete_project(project):
    # import pdb;pdb.set_trace()
    try:
        status = project.get_status()
        services = project.services
        if services:
            for sproject in list(services):
                if status < CONFIRMED:
                    sproject.delete()
                else:
                    sproject.status = DISABLED
                    sproject.save()

        if status < CONFIRMED:
            project.delete()
            response = dict(status='ok', id=unicode(project.pk), msg="Project deleted.")
        else:
            response = dict(status='ok', id=unicode(project.pk), msg="Project disabled.")
        return respond_json(response, status=200)

    except Exception, e:
        response = dict(status='fail', msg=unicode(e))
        return respond_json(response, status=400)


def update_project(project, item, is_new=False):
    # import pdb;pdb.set_trace()
    _status = SAVED
    status_code = 200
    if is_new: status_code = 201
    try:
        resp = regex_name(item)
        if resp is not None: return resp
        if 'name' not in item:
            item['name'] = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        client = None
        client_id = item.pop('client', None)
        if client_id:
            is_provider = get_type_user(client_id)
            if is_provider:
                client = Provider.objects.get(id=client_id); _status = CONFIRMED
            else:
                client = Client.objects.get(id=client_id)
        if project.client:
            if client and project.client != client:
                return error_api(msg='Error: Client project can not be changed.', status=400)
        elif client is None:
            return error_api("Client not defined.", status=400)
        else:
            project.client = client

        services = project.services
        if services:
            for sproject in list(services):
                sproject.delete()
                project.services.remove(sproject)

        sitems = item.pop('services')

        for name in ['name', 'description', 'summary']:
            if name in item:
                setattr(project, name, item[name])
        try:
            project.save()
        except NotUniqueError:
            error_response = create_message_error(409, 'NOT_UNIQUE_PROJECT_NAME')
            return respond_json(error_response, status=409)

        services = []
        if not sitems:
            project.delete()
            return error_api("No services.", status=400)
        try:
            for sitem in sitems:
                service_id = sitem['service']
                # service = ServiceDescription.objects.get(id=service_id)
                service = get_db(_cfg.database__database_name)['services']. \
                    find_one({'_id': ObjectId(service_id)})
                if service is None:
                    project.delete()
                    return error_api("Service '%s' doesn't exist." % service_id, status=400)
                services.append(service)
        except Exception, err:
            project.delete()
            return error_api(msg="Error in project '%s'." % err, status=400)
        try:
            for sitem, service in zip(sitems, services):
                # context_type=sitem.get('context_type', '')
                provider = service['provider']
                sproject = SProject(service=service['_id'],
                                    project=project,
                                    provider=provider,
                                    status=_status)
                sproject.save()
                project.services.append(sproject)
            project.save()
        except Exception, err:
            if project.services:
                for sproject in project.services:
                    sproject.delete()
                project.delete()
                return error_api(msg="Error: updating project '%s'." % err, status=400)
        response = dict(status=project.status, id=unicode(project.pk), name=project.name,
                        created=project.created_at)
        return respond_json(response, status=status_code)
    except Exception, e:
        response = dict(status='fail', msg=unicode(e))
        return respond_json(response, status=400)


def create_project(item):
    project = Project()
    return update_project(project, item, is_new=True)


def save_image_to_local(vm_image, vm_name):
    image = VMImage(vm_name)
    image.id = ObjectId(vm_image)
    name_id = image.get_image()
    return _cfg.repository__ip + name_id


def find_instance(id):
    instance = get_db(_cfg.database__database_name)['instances'].find_one({'sproject': ObjectId(id)})
    return instance


def get_status(state):
    _status = dict(STATUS)
    return list(_status.keys())[list(_status.values()).index(state)]


def get_type_user(id):
    cursor = get_db(_cfg.database__database_name)['users'].find_one({'_id': ObjectId(id)})
    if cursor['_cls'] == 'User.Provider':
        return True
    return False
