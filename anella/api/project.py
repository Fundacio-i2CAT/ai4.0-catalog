# -*- coding: utf-8 -*-

from bson import ObjectId
import os
from anella.common import *
from anella.model.project import Project, SProject, SAVED, DISABLED, CONFIRMED, STATES, STATUS, Client, ServiceDescription
from anella.model.instance import Instance
from anella.model.service import VMImage

from anella.orch import Orchestrator
from anella.api.utils import Resource, ColRes, ItemRes, respond_json, error_api, item_to_json
from anella import configuration as _cfg
import json

def services_to_json(sprojects):
    sitems=[]
    for service_id in sprojects:
        sproject = get_db(_cfg.database__database_name)['sprojects'].find_one({'_id':service_id})
        sitem = item_to_json(sproject, ['_id', 'context_type', 'status', 'provider', 'created_at' ])
        service = get_db(_cfg.database__database_name)['services'].find_one({'_id':sproject['service']})
        provider = get_db(_cfg.database__database_name)['users'].find_one({'_id':service['provider']})

        sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
        # sitem['service'] = item_to_json(service, ['_id', 'name'])
        sitem['service'] = item_to_json(service, ['_id', 'name'])
        sitems.append(sitem)

    return sitems

def sprojects_to_json(sprojects):
    # import pdb;pdb.set_trace()
    sitems=[]
    for sproject in sprojects:
        sitem = sproject_to_json(sproject)
        sitems.append(sitem)
    
    return sitems

def sproject_to_json(sproject, context=False):
    project = get_db(_cfg.database__database_name)['projects'].find_one({'_id':sproject['project']})
    sitem = item_to_json(sproject, ['_id', 'status', 'created_at' ])
    service = get_db(_cfg.database__database_name)['services'].find_one({'_id':sproject['service']})
    provider = get_db(_cfg.database__database_name)['users'].find_one({'_id':service['provider']})
    client = get_db(_cfg.database__database_name)['users'].find_one({'_id':project['client']})

    sitem['project'] = item_to_json(project, ['_id', 'name'])
    sitem['client'] = item_to_json(client, ['_id', 'user_name'])
    sitem['provider'] = item_to_json(provider, ['_id', 'user_name'])
    # sitem['service'] = item_to_json(service, ['_id', 'name'])
    sitem['service'] = item_to_json(service, ['_id', 'name'])

    if context:
        sitem.update( item_to_json(sproject, ['context_type', 'context']) )

    return sitem


def get_service(id_service):
    return get_db(_cfg.database__database_name)['services'].find_one({'_id': id_service})

def get_service_by_objectid(id_service):
    return get_db(_cfg.database__database_name)['services'].find_one({'_id': ObjectId(id_service)})

class ProjectStatesRes(Resource):
    def get(self):
        return [ dict(status=st[0], name=st[1]) for st in STATUS]

class ProjectsRes(ColRes):
    collection= 'projects'
    _cls = Project
    name= 'Projects'
    fields = '_id,name,summary,client,status,services,created_at,updated_at'.split(',')
    filter_fields = 'name,status'.split(',')

    def _item_to_json(self, item):
        services = item.get('services')
        project = self._find_obj(item['_id'])
        item['status'] = project.get_status()
        item['services'] = services_to_json(services)
        return item_to_json(item, self.fields)

    def get(self):
        return ColRes.get(self)

    def post(self):
        item = get_json()
        return create_project(item)

class ProjectRes(ItemRes):
    collection= 'projects'
    _cls = Project
    name= 'Project'
    fields = '_id,name,summary,description,client,services,status,created_at,created_by,updated_at,updated_by'.split(',')

    def _item_to_json(self, item):
        project = self._find_obj(item['_id'])
        item['status'] = project.get_status()
        services = item.get('services')
        item['services'] = services_to_json(services)
        return item_to_json(item, self.fields)


    def put(self, id):
        """ Modifies the project when not confirmed.
            Use Project/state othercase
        """
        # import pdb;pdb.set_trace()
        project = self._find_obj(id)
        if not project:
            return error_api( msg='Error: wrong project id in request.', status=404 )
        status = project.get_status()
        if status >= CONFIRMED:
            return error_api( msg='Error: project is confirmed yet.', status=400 )

        item = get_json()
        return update_project(project, item)

    def delete(self, id):
        project = self._find_obj(id)
        if not project:
            return error_api( msg='Error: wrong project id in request.', status=404 )
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
            #Save consumer params in SProjects
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

                elif not self.orch.instance_set_state(instance['instance_id'], state):
                    return "Error instance '%s' set_state." % instance['instance_id']

            elif state!='DISABLED':
                #context para el orquestrador
                service = get_service(item['service'])
                context = service['context']
                #name_image = context['name_image']
                # Primero miramos si está la imagen cacheada en el orquestrador
                if self.exists_image(context):
                    context['vm_image'] = _cfg.repository__ip + context['name_image']
                else:
                    # Si no lo está. GUardamos la imagen en local
                    context['vm_image'] = save_image_to_local(context['vm_image'], context['name_image'])
                #guardada la imagen. Seguimos
                context['consumer_params'] = self.consumer_params
                context = dict(context=context)
                instance_id = self.orch.instance_create(context)
                if instance_id:
                    instance = Instance(sproject=sproject, instance_id=instance_id)
                    instance.save()
                    # delete local image
                    #path_file = "{0}{1}".format(_cfg.repository__path, name_image)
                    #os.remove(path_file)
                else:
                    return "Error instance create."

        status,error = self._get_state(services)
        if self.orch.req.status_code not in (200,201):
            return "Error instance create."

    def exists_image(self, service):
        context = dict(popid=1)
        if 'popid' in service:
            context['popid'] = service['popid']
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
                project_status=DISABLED
                break
            if instance:
                data = self.orch.instance_get_state(instance['instance_id'])
                state = data['state']
                if self.orch.req.status_code not in (200,201):
                    return '','Error in get project status.'

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
                    return '',''
            # some error
            break

        if (project_status is None) or (data is None):
            return '',''
        else:
            return dict(status=project_status, state=STATES[project_status], runtime_params=data['runtime_params']),''
            

    def get(self, id):
        # import pdb;pdb.set_trace()
        self.project = self._find_obj(id)
        if not self.project:
            return error_api( msg='Error: wrong project id in request.', status=404 )
        status = self.project.get_status()
        if status < CONFIRMED:
            response = dict(state= STATES[status], status=status, project_id=id)
            return respond_json( response, status=200)

        state,error = self._get_state(self.project.services)
        if error:
            return error_api( msg=error, status=400 )
        if state:
            return respond_json({"state": state, "project_id": id}, status=200)
        else:
            response = dict( state='CONFIRMED', status=3, project_id=id)
            return respond_json( response, status=200)

    def put(self, id):
        # import pdb;pdb.set_trace()
        self.project = self._find_obj(id)
        if not self.project:
            return error_api( msg='Error: wrong project id in request.', status=404 )
        status = self.project.get_status()
        if status < CONFIRMED:
            return error_api( msg='Error: project is not confirmed yet.', status=400 )

        data = get_json()
        status = data.get('status')
        if status not in range(len(STATES)):
            return error_api( msg='Error: wrong status in request.', status=400 )
        state = STATES[status]
        if state not in  STATES:
            return error_api( msg='Error: wrong status in request.', status=400 )
        # In any case ensure instances exist
        self.consumer_params = data.get('consumer_params')
        error = self._set_state(self.project.services, state )

        if error:
            return error_api( msg="Error: '%s' in request." % error, status=400 )
        else:
            response = dict( status='ok', msg="Project state set to '%s'" % state )
            return respond_json( response, status=200)


class ProjectUpdateStateRes(ProjectRes):
    def __init__(self):
        self.orch = Orchestrator(debug=False)
        self.spres = SProjectRes()

    def put(self, id):
        # import pdb;pdb.set_trace()
        self.project = self._find_obj(id)
        if not self.project:
            return error_api( msg='Error: wrong project id in request.', status=404)

        data = get_json()
        status = data.get('status')
        if status not in range(len(STATES)):
            return error_api( msg='Error: wrong status in request.', status=400 )
        state = STATES[status]
        if state not in  STATES:
            return error_api( msg='Error: wrong status in request.', status=400 )
        # In any case ensure instances exist
        error = self._update_state(self.project.services, state)

        if error:
            return error_api( msg="Error: '%s' in request." % error, status=400 )
        else:
            response = dict( status='ok', msg="Project state set to '%s'" % state )
            return respond_json( response, status=200)

    def _update_state(self, services, state):
        # Services are items (not obj)
        # import pdb;pdb.set_trace()
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

                elif not self.orch.instance_set_state(instance['instance_id'], state):
                    return "Error instance '%s' set_state." % instance['instance_id']

class ClientProjectsRes(ProjectsRes):

    def get(self, id):
        self.client_id=id
        return super(ClientProjectsRes, self).get()

    def _get_items(self, skip=0, limit=1000):
        values = get_args().copy() # args are inmutable
        # status = int(values and values.pop('status', 0)) or None
        filter = self._filter_from_inputs(values)
        filter['client'] = ObjectId(self.client_id)
        cursor = get_db(_cfg.database__database_name)['projects'].find(filter, skip=skip, limit=limit )
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
        item['status'] = project.get_status()
        item['services'] = services_to_json(services)
        return item_to_json(item, self.fields)


class SessionProjectRes(ProjectRes):
    collection= 'projects'
    _cls = Project
    name= 'Project'
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
    collection= 'sprojects'
    _cls = SProject
    name= 'Service Contract'
    fields = '_id,service,status,created_at,updated_at'.split(',')
#     filter_fields = 'name'.split(',')

    def post(self, id):
        try:
            project = Project.objects.get(id=ObjectId(id))
            obj = self._obj_from_json(get_json())
            obj.project = project
            valid_error = self._validate(obj)
            if valid_error:
                response = dict( status='fail', msg='%s: %s' % (self.name,valid_error))
                return respond_json( response, status=400)

            obj.save()
            response = dict( status='ok', msg='%s updated' % self.name )
            return respond_json( response, status=200)

        except Exception,e:
            return error_api( msg=str(e) )
        

    def get(self, id):
        project = get_db(_cfg.database__database_name)['projects'].find_one({'_id':ObjectId(id)})
        result = services_to_json(project['services'])
        response = dict( status='ok', result=result )
        return respond_json( response, status=200)

class SProjectsRes(ColRes):
    collection= 'sprojects'
    _cls = SProject
    name= 'SProjects'
    fields = '_id,project,service,context,created_at'.split(',')

    def item_from_json(self, data):
        service_cls = get_service_cls( data.get('service_type') )
        if service_cls:
            self._cls = service_cls
        item = ColRes.item_from_json(self, data)
        item['_cls'] = service_cls._class_name
        # obj = service_cls.from_json(item)
        return item

class SProjectRes(ItemRes):
    collection= 'sprojects'
    _cls = SProject
    name= 'SProject'
    fields = 'project,service,context_type,context,created_at'.split(',')

    def _item_to_json(self, item):
        return sproject_to_json(item)

    def put(self, id):
        # import pdb;pdb.set_trace()
        self.sproject = self._find_obj(id)
        if not self.sproject:
            return error_api( msg='Error: wrong service project id in request.', status=404 )
        data = get_json()
        status = data.get('status')
        if status not in [CONFIRMED, DISABLED]: # Only support confirm by now. not in range(len(STATES)):
            return error_api( msg='Error: wrong status in request.', status=400 )

        if status==CONFIRMED and self.sproject.status in range(CONFIRMED, DISABLED):
            return error_api( msg='Error: service project is already confirmed yet.', status=400 )

#         if status==DISABLED and self.sproject.status < CONFIRMED, DISABLED):
#             return error_api( msg='Error: service project is already confirmed yet.', status=400 )

        state = STATES[status]
        self.sproject.status= status
        self.sproject.save()
        response = dict( status='ok', msg="Service project state set to %s" % state )
        return respond_json( response, status=200)

class ProviderSProjectsRes(SProjectsRes):
    filter_fields = 'provider,status'.split(',')

    def get(self, id):
        # import pdb;pdb.set_trace()
        self.provider_id=id
        return super(ProviderSProjectsRes, self).get()

    def _filter_from_inputs(self, values):
        # import pdb;pdb.set_trace()
        filter = super(ProviderSProjectsRes, self)._filter_from_inputs(values)
        filter['provider'] = ObjectId(self.provider_id)
        return filter

    def _get_items(self, skip=0, limit=1000):
        # import pdb;pdb.set_trace()
        values = get_args().copy() # args are inmutable
        # status = int(values and values.pop('status', 0)) or None
        filter = self._filter_from_inputs(values)
        filter['provider'] = ObjectId(self.provider_id)
        cursor = get_db(_cfg.database__database_name)['sprojects'].find(filter, skip=skip, limit=limit )
        return [item for item in cursor ]

    def _items_to_json(self, items):
        return sprojects_to_json(items)

class ProjectOrchCallbackRes(ProjectsRes):

    def post(self):
        instance_info = get_json()
        if 'image_path' in instance_info:
            try:
                file_to_remove = '{0}/{1}'.format(_cfg.repository__path,
                                                  instance_info['image_path'])
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
                if status<CONFIRMED:
                    sproject.delete()
                else:
                    sproject.status=DISABLED
                    sproject.save()

        if status<CONFIRMED:
            project.delete()
            response = dict( status='ok', id=unicode(project.pk), msg="Project deleted." )
        else:
            response = dict( status='ok', id=unicode(project.pk), msg="Project disabled." )
        return respond_json( response, status=200)

    except Exception,e:
        response = dict( status='fail', msg=unicode(e) )
        return respond_json( response, status=400)

                

def update_project(project, item, is_new=False):
    # import pdb;pdb.set_trace()
    try:
        client = None
        client_id = item.pop('client',None)
        if client_id:
            client = Client.objects.get(id=client_id)
        if project.client:
            if client and project.client!=client:
                return error_api( msg='Error: Client project can not be changed.', status=400 )
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
     
        project.save()

        services=[]
        if not sitems:
            return error_api("No services.", status=400)
        for sitem in sitems:
            service_id = sitem['service']
            #service = ServiceDescription.objects.get(id=service_id)
            service = get_db(_cfg.database__database_name)['services'].\
                find_one({'_id': ObjectId(service_id)})
            if service is None:
                return error_api("Service '%s' doesn't exist." % service_id, status=400)
            services.append(service)


        try:
            for sitem,service in zip(sitems,services):
                #context_type=sitem.get('context_type', '')
                provider = service['provider']
                sproject = SProject(service=service['_id'],
                                    project=project,
                                    provider=provider,
                                    status=SAVED )
                sproject.save()
                project.services.append(sproject)
        except Exception,err:
            if project.services:
                for sproject in project.services:
                    sproject.delete()
            project.delete()
            return error_api( msg="Error: updating project '%s'." % err, status=400 )
        else:
            project.save()

        if is_new:
            response = dict( status='ok', id=unicode(project.pk), msg="Project created." )
            return respond_json(response, status=201)
        else:
            response = dict( status='ok', id=unicode(project.pk), msg="Project updated." )
            return respond_json(response, status=200)

    except Exception,e:
        response = dict( status='fail', msg=unicode(e) )
        return respond_json(response, status=400)


def create_project(item):
    project = Project()
    return update_project(project, item, is_new=True)


def save_image_to_local(vm_image, vm_name):
    image = VMImage(vm_name)
    image.id = ObjectId(vm_image)
    image.get_image()
    return _cfg.repository__ip + vm_name


def find_instance(id):
    instance = get_db(_cfg.database__database_name)['instances'].find_one({'sproject':ObjectId(id)})
    return instance
