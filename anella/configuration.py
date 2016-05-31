"""
Configuration parameters for anella package.
Loaded at init so modules can use them.
"""

admin__user = None
admin__email = None
admin__sendmail = None

app__host = None
app__port = None

database__host = None
database__port = None
database__database_name = None
database__collection_config = None
database__collection_log = None

# Authentication Service
auth__host = None
auth__port = None

# Orchestrator Manager Service
orch__host = None
orch__port = None

# OpenStack (?)
openstack__auth_url = None
openstack__username = None
openstack__password = None
openstack__tenant = None

# MQ ?
# mq__host = None
# mq__port = None
# mq__exchange = None
# mq__inbound = None
# mq__outbound = None
# mq__username = None
# mq__password = None

# plugin_java = None
# plugin_python = None
# plugin_cpp = None
# plugin__grouping = None
# plugin__default_weighting = None
# plugin__weightings = None

heat_resource_mq__host = None
heat_resource_mq__port = None
heat_resource_mq__username = None
heat_resource_mq__password = None
heat_resource_mq__exchange = None
heat_resource_mq__key = None

openstack_event__host = None
openstack_event__port = None
openstack_event__username = None
openstack_event__password = None
openstack_event__exchange = None
openstack_event__key = None

app_feedback__host = None
app_feedback__port = None
app_feedback__username = None
app_feedback__password = None
app_feedback__exchange = None
app_feedback__key = None
