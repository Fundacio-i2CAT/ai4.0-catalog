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

repository__path = None
repository__ip = None
repository__download = None

tenor__host = None
tenor__port = None

errors__orchestrator_state = None
