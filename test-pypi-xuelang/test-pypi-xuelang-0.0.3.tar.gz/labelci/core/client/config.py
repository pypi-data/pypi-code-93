import os

DEFAULT_REQUEST_TIMEOUT = 200

# Token
GET_TOKEN = "/api/current-user/token"

# Project API
GET_PROJECT = "/api/projects/{}"
GET_PROJECT_LIST = "/api/projects/"
CREATE_PROJECT = "/api/projects/"
VALIDATE_LABEL_CONFIG = "/api/projects/validate/"
GET_PROJECT_ID = "/api/projects/{}/"
UPDATE_PROJECT = "/api/projects/{}/"
DELETE_PROJECT = "/api/projects/{}/"
GET_PROJECT_TASKS = "/api/projects/{}/tasks/"
DELETE_ALL_TASKS = "/api/projects/{}/tasks/"
VALIDATE_PROJECT_LABEL_CONFIG = "/api/projects/{}/validate/"
GET_LABEL_CONFIG_TEMPLATE = "/api/templates"

# Data export API
PROJECT_EXPORT = "/api/projects/{}/export"
GET_EXPORT_FORMATS = "api/projects/{}/export/formats"