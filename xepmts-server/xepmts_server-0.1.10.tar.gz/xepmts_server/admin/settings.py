
import os
from xepmts_server.secrets import MONGO_PASSWORD

VERSIONS = ['v1', 'v2', 'sc']

SERVER_SCHEMA = {
    'name': { 'type': 'string', 'nullable': False, 'unique': True},
    'url': { 'type': 'string', 'nullable': False, 'unique': True},

}

RESOURCE_SCHEMA = {
 'name': { 'type': 'string', 'nullable': False, 'unique': True},
 'url': { 'type': 'string', 'nullable': False, 'unique': True},
 'resource_methods': { 'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
 'public_methods': { 'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
 'item_methods': { 'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
 'public_item_methods': { 'type': 'list', 'schema': {'type': 'string'}, },
 'allowed_roles': { 'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
 'allowed_read_roles': { 'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
 'allowed_write_roles': { 'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
 'cache_control': { 'type': 'string', 'default': ''},
 'cache_expires': { 'type': 'integer', 'default': 0 },
 'id_field': { 'type': 'string', 'default': '_id'},
 'item_lookup_field': { 'type': 'string', 'default': '_id'},
 'item_url': { 'type': 'string', 'default': 'regex("[a-f0-9]{24}")'},
 'resource_title': { 'type': 'string', 'required': True},
 'item_title': { 'type': 'string', 'required': True},
 'item_lookup': { 'type': 'boolean', 'default': True},
 'allowed_item_roles': { 'type': 'list', 'schema': {'type': 'string'}},
 'allowed_item_read_roles': { 'type': 'list', 'schema': {'type': 'string'}},
 'allowed_item_write_roles': { 'type': 'list', 'schema': {'type': 'string'}},
 'allowed_filters': { 'type': 'list', 'schema': {'type': 'string'}, 'default': ['*']},
 'sorting': { 'type': 'boolean', 'default': True},
 'embedding': { 'type': 'boolean', 'default': True},
 'embedded_fields': { 'type': 'list', 'schema': {'type': 'string'}, 'default': []},
 'pagination': { 'type': 'boolean', 'default': True},
 'projection': { 'type': 'boolean', 'default': True},
 'versioning': { 'type': 'boolean', 'default': False},
 'soft_delete': { 'type': 'boolean', 'default': False},
 'bulk_enabled': { 'type': 'boolean', 'default': True},
 'internal_resource': { 'type': 'boolean', 'default': False},
 'etag_ignore_fields': { 'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
 'auth_field': { 'type': 'string', 'nullable': True},
 'allow_unknown': { 'type': 'boolean', 'default': False},
 'extra_response_fields': { 'type': 'list', 'schema': {'type': 'string'}, 'default': []},
 'mongo_query_whitelist': { 'type': 'list', 'schema': {'type': 'string'}, 'default': []},
 'mongo_write_concern':  { 'type': 'dict', 'default': {'w': 1}},
 'mongo_indexes': { 'type': 'dict', 'default': {}},
 'mongo_prefix': {'type': 'string', 'nullable': True},
 'hateoas': { 'type': 'boolean', 'default': True},
 'merge_nested_documents': { 'type': 'boolean', 'default': True},
 'normalize_dotted_fields': { 'type': 'boolean', 'default': True},
 'normalize_on_patch': { 'type': 'boolean', 'default': True},
 'schema': {'type': 'dict', 'required': True },
 'datasource': {
     'type': 'dict',
     'schema': {
          'source': {'type': 'string', },
          'filter': {'type': 'dict', 'nullable': True},
          'default_sort': {'type': 'string', 'nullable': True },
          'projection': {'type': 'dict', 'nullable': True},
          'aggregation': {'type': 'dict', 'nullable': True},
     }
               },
'additional_lookup': {'oneof': [{'type': 'string'}, {'type': 'dict'}], 'nullable': True},

}


DOMAIN = {
    v: {
        'schema': RESOURCE_SCHEMA,
        'datasource': {'source': f'{v}_endpoints'},
        'public_methods': ['GET'],
        'allowed_item_write_roles' : ['admin'],
        'allow_unknown': True,
        'additional_lookup': {
            'url': 'regex("[\w]+")',
            'field': 'name'
            }}
    for v in VERSIONS}

DOMAIN['servers'] = {
    'schema': SERVER_SCHEMA,
    'allowed_item_write_roles' : ['admin'],
    'allow_unknown': True,
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'name'
            },
}    

URL_PREFIX = os.getenv("XEPMTS_URL_PREFIX", "")
API_VERSION = "admin"
RESOURCE_METHODS = ["GET", "POST"]
ITEM_METHODS = ["GET", "PUT", "PATCH", "DELETE"]
ALLOWED_READ_ROLES = ["admin", "superuser", "expert", "user", "read", "write"]
ALLOWED_WRITE_ROLES = ["admin", "superuser", "expert", "write"]
EMBEDDING = True
MEDIA_PATH = "files"
PAGINATION_LIMIT = 10000
SCHEMA_ENDPOINT = "schema"
IF_MATCH = True
ENFORCE_IF_MATCH = False
HATEOAS = True
VERSIONS = "_versions"
NORMALIZE_ON_PATCH = False
ALLOW_UNKNOWN = True
# ----------------- Mongo config ------------------------------------------ #
MONGO_HOST = os.getenv("XEPMTS_MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("XEPMTS_MONGO_PORT", 27017))
MONGO_DBNAME = os.getenv("XEPMTS_MONGO_DB", "pmts")
MONGO_USERNAME = os.getenv("XEPMTS_MONGO_USER", "")
MONGO_AUTH_SOURCE = os.getenv("XEPMTS_MONGO_AUTH_SOURCE", MONGO_DBNAME)

X_HEADERS = ['Content-Type', 'If-Match', 'Authorization', 'X-HTTP-Method-Override']  # Needed for the "Try it out" buttons

JWT_AUDIENCES = os.getenv("XEPMTS_JWT_AUDIENCES", "https://api.pmts.xenonnt.org").split(",")
JWT_KEY_URL = os.getenv("XEPMTS_JWT_KEY_URL", "https://auth-dot-xenon-pmts.uc.r.appspot.com/.well-known/jwks.json")
JWT_SCOPE_CLAIM = os.getenv("XEPMTS_JWT_SCOPE_CLAIM","scope")
JWT_ROLES_CLAIM = os.getenv("XEPMTS_JWT_ROLES_CLAIM", "roles")
JWT_TTL = 3600
