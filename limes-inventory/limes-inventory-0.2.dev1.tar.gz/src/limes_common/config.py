from pytz import timezone

TIME_ZONE = timezone('Canada/Pacific')
ENCODING = 'utf-8'

# CSRF_NAME = 'csrfmiddlewaretoken'
CSRF_NAME = 'X-CSRFToken'

# ELAB_URL = 'https://us.elabjournal.com/'
ELAB_URL = 'https://elab.msl.ubc.ca/'
ELAB_API = '%sapi/v1/' % ELAB_URL

SERVER_API_VER = 'd1'
# SERVER_BIND = '127.0.0.1:8001'
SERVER_BIND = 'sh-lims.microbiology.ubc.ca:8001'
SERVER_URL = 'http://%s/api/%s/' % (SERVER_BIND, SERVER_API_VER)
SERVER_DB_PATH = 'limes_server/db'

# PROVIDER_STATICS_PATH = 'limes_core/example_static_providers.json'
PROVIDER_STATICS_PATH = 'limes_core/static_providers.json'
PROVIDER_DEFAULT_TRANSACTION_TIMEOUT = 5
PROVIDER_DEFAULT_CONNECTION_TIMEOUT = 60
PROVIDER_DEFAULT_CRTIERIA = 'ALL'