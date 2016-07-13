# -*- coding: utf-8 -*-

from bson import ObjectId

from anella.common import *
from anella.model.project import Project, SProject, DISABLED, CONFIRMED, STATES, STATUS, Client, ServiceDescription
from anella.model.instance import Instance

from anella.orch import Orchestrator
from anella.api.utils import Resource, ColRes, ItemRes, respond_json, error_api, item_to_json

def services_to_json(sprojects):
    sitems=[]
    for service_id in sprojects:
        sproject = get_db()['sprojects'].find_one({'_id':service_id})
        sitem = item_to_json(sproject, ['_id', 'context_type', 'status', 'provider', 'created_at' ])
        service = get_db()['services'].find_one({'_id':sproject['service']})
        provider = get_db()['partners'].find_one({'_id':service['provider']})

        sitem['provider'] = item_to_json(provider, ['_id', 'name'])
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
    project = get_db()['projects'].find_one({'_id':sproject['project']})
    sitem = item_to_json(sproject, ['_id', 'status', 'created_at' ])
    service = get_db()['services'].find_one({'_id':sproject['service']})
    client = get_db()['partners'].find_one({'_id':service['provider']})

    sitem['project'] = item_to_json(project, ['_id', 'name'])
    sitem['client'] = item_to_json(client, ['_id', 'name'])
    # sitem['service'] = item_to_json(service, ['_id', 'name'])
    sitem['service'] = item_to_json(service, ['_id', 'name'])

    if context:
        sitem.update( item_to_json(sproject, ['context_type', 'context']) )

    return sitem

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
        return delete_project(project)


class ProjectStateRes(ProjectRes):

    def __init__(self):
         self.orch = Orchestrator(debug=True)
         self.spres = SProjectRes()

    def _find_instance(self, id):
        instance = get_db()['instances'].find_one({'sproject':ObjectId(id)})
        return instance

    def _set_state(self, services, state):
        # Services are items (not obj)
        # import pdb;pdb.set_trace()
        for sproject in services:
            service_id = unicode(sproject.pk)
            item = self.spres._find_item(unicode(sproject.pk))
            instance = self._find_instance(unicode(item['_id']))
            if instance:
#                 if self.orch:
                if state=='DISABLED':
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
                service = sproject_to_json(item, context=True)
                del service['_id']
                del service['status']
                del service['created_at']
                instance_id = self.orch.instance_create(service)
                if instance_id:
                    instance = Instance(sproject=sproject, instance_id=instance_id)
                    instance.save()

    def _get_state(self, services):
        # Services are items (not obj)
        # import pdb;pdb.set_trace()
        project_status = None
        for sproject in services:
            service_id = unicode(sproject.pk)
            item = self.spres._find_item(unicode(service_id))
            instance = self._find_instance(unicode(item['_id']))
            if sproject.status== DISABLED:
                project_status=DISABLED
            if instance:
                state = self.orch.instance_get_state(instance['instance_id'])
                if state:
                    status = STATES.index(state)
                    if project_status is None or status < project_status:
                        project_status = status
                    continue
            # some error
            break

        if project_status is None:
            return ''
        else:
            return STATES[project_status]
            

    def get(self, id):
        # import pdb;pdb.set_trace()
        self.project = self._find_obj(id)
        if not self.project:
            return error_api( msg='Error: wrong project id in request.', status=404 )
        status = self.project.get_status()
        if status < CONFIRMED:
            response = dict( state= STATES[status], status=status )
            return respond_json( response, status=200)

        state = self._get_state(self.project.services)
        if state:
            status = STATES.index(state)
            response = dict( state=state, status=status )
            return respond_json( response, status=200)
        else:
            response = dict( state='CONFIRMED', status=3 )
            return respond_json( response, status=200)
#             return error_api( msg="Error: Getting state.", status=400 )

        
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
        error = self._set_state(self.project.services, state )

        if error:
            return error_api( msg="Error: '%s' in request." % error, status=400 )
        else:
            response = dict( status='ok', msg="Project state set to '%s'" % state )
            return respond_json( response, status=200)


class ClientProjectsRes(ProjectsRes):

    def get(self, id):
        self.client_id=id
        return super(ClientProjectsRes, self).get()

    def _get_items(self, skip=0, limit=1000):
        values = get_args().copy() # args are inmutable
        # status = int(values and values.pop('status', 0)) or None
        filter = self._filter_from_inputs(values)
        filter['client'] = ObjectId(self.client_id)
        cursor = get_db()['projects'].find(filter, skip=skip, limit=limit )
        return [item for item in cursor ]

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
        project = get_db()['projects'].find_one({'_id':ObjectId(id)})
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
        if status != CONFIRMED: # Only support confirm by now. not in range(len(STATES)):
            return error_api( msg='Error: wrong status in request.', status=400 )

        if status and self.sproject.status >= CONFIRMED:
            return error_api( msg='Error: service project is already confirmed yet.', status=400 )

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
        cursor = get_db()['sprojects'].find(filter, skip=skip, limit=limit )
        return [item for item in cursor ]

    def _items_to_json(self, items):
        return sprojects_to_json(items)

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

        if status<CONFIRMED:
            project.delete()

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
        services=[]
        if not sitems:
            return error_api("No services.", status=400)
        for sitem in sitems:
            service_id = sitem['service']
            service = ServiceDescription.objects.get(id=service_id)
            if service is None:
                return error_api("Service '%s' doesn't exist." % service_id, status=400)
            services.append(service)

        for name,value in item.items():
            setattr(project, name, value)

        project.save()

        try:
            for sitem,service in zip(sitems,services):
                context_type=sitem.get('context_type', '')
                context=sitem.get('context',{})
    
                if not context_type:
                    context_type= service.properties.get('context_type', '')
                    if not context_type:
                        return error_api("Context_type not defined.", status=400)
    
                if not context:
                    if context_type:
                        scontext = get_db()['scontexts'].find_one({'context_type':context_type})
                        context=scontext['context']
                    else:
                        context={}
    
                sproject = SProject(service=service,
                                    project=project,
                                    provider=service.provider,
                                    context_type=context_type,
                                    context=context)
    
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
            return respond_json( response, status=201)
        else:
            response = dict( status='ok', id=unicode(project.pk), msg="Project updated." )
            return respond_json( response, status=200)

    except Exception,e:
        response = dict( status='fail', msg=unicode(e) )
        return respond_json( response, status=400)


def create_project(item):
    # import pdb;pdb.set_trace()
    project = Project()
    return update_project(project, item, is_new=True)

