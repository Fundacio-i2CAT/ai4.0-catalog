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
database__database_repository = None

# Authentication Service
auth__host = None
auth__port = None
auth__eurecat = None
auth__oauth = None

# Orchestrator Manager Service
orch__host = None
orch__port = None
orch__url = None

# Mail
mail__from = None
mail__to = None
mail__pass = None
mail__port = None
mail__smtp = None
mail__subject = None
mail__body = None
mail__owner = None
mail__developer = None
mail__ban = None
mail__welcome = None
mail__notify = None
mail__system = None

repository__path = None
repository__ip = None
repository__download = None

tenor__host = None
tenor__port = None

errors__orchestrator_state = None

keystone__url = None
keystone__file = None
keystone__login = None
keystone__data_login = None
keystone__project_name = None
keystone__data_create_user = None
keystone__create_user = None
keystone__data_patch_user = None
keystone__data_patch_password_user = None
keystone__data_change_password_user = None

