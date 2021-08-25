import os
from pathlib import Path
from typing import Text

__NEURALSPACE_URL = "https://ns-platform-staging.uksouth.cloudapp.azure.com"
NEURALSPACE_URL_ENV_VAR = "NEURALSPACE_URL"
LOGIN_URL = "api/auth/login"
INSTALL_APP_URL = "api/app/install"

COMMON_HEADERS = {
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
}

NAME_GENERATOR_CONFIG = {
    "adj": ("emotions", "age", "character"),
}

# Literals to be used globally
NEURALSPACE_PATH_ENV_VAR = "NEURALSPACE_PATH"

# Panini default data directory
__NEURALSPACE_HOME = Path.home() / ".neuralspace"


def neuralspace_home() -> Path:
    global __NEURALSPACE_HOME

    if NEURALSPACE_PATH_ENV_VAR in os.environ:
        __NEURALSPACE_HOME = Path(os.environ[NEURALSPACE_PATH_ENV_VAR])

    # Create directory if doesn't exist
    __NEURALSPACE_HOME.mkdir(parents=True, exist_ok=True)
    return __NEURALSPACE_HOME


def neuralspace_url() -> Text:
    global __NEURALSPACE_URL

    if NEURALSPACE_URL_ENV_VAR in os.environ:
        __NEURALSPACE_URL = os.environ[NEURALSPACE_URL_ENV_VAR]

    return __NEURALSPACE_URL


def auth_path() -> Path:
    return neuralspace_home() / "auth.json"


# KEYS

PROJECT_ID = "projectId"
LANGUAGE = "language"
LANGUAGES = "languages"
TYPE = "type"
EXAMPLE = "example"
VALUE = "value"
START_INDEX = "start_idx"
END_INDEX = "end_idx"
TIME = "time"
FROM = "from"
TO = "to"
AUTHORIZATION = "Authorization"
PROJECT_NAME = "projectName"
SEARCH = "search"
PAGE_NUMBER = "pageNumber"
PAGE_SIZE = "pageSize"
DATA = "data"
DELETED = "deleted"
NOT_FOUND = "notFound"
PROJECTS = "projects"
NUMBER_OF_EXAMPLES = "noOfExamples"
NUMBER_OF_INTENTS = "noOfIntents"
NUMBER_OF_MODELS = "noOfModels"
FILTER = "filter"
PREPARED = "prepared"
COUNT = "count"
CREATED_AT = "createdAt"
ENTITIES = "entities"
INTENT = "intent"
EXAMPLE_ID = "exampleId"
TEXT = "text"
EXAMPLES = "examples"
MODEL_NAME = "modelName"
MODEL_ID = "modelId"
TRAINING_STATUS = "trainingStatus"
COMPLETED = "Completed"
FAILED = "Failed"
TIMED_OUT = "Timed Out"
DEAD = "Dead"
REPLICAS = "replicas"
METRICS = "metrics"
INTENT_CLASSIFIER_METRICS = "intentClassifierPerformance"
INTENT_ACCURACY = "i_acc"
NER_METRICS = "nerPerformance"
ENTITY_ACC = "e_acc"
TRAINING_TIME = "trainingTime"
MESSAGE = "message"
MODELS = "models"
N_REPLICAS = "nReplicas"
LAST_STATUS_UPDATED = "lastStatusUpdateAt"
PARSED_RESPONSE = "parsedResponse"
OUTPUT = "output"
YES = "Yes"
NO = "No"

# Follow up Commands
CREATE_PROJECT_COMMAND = "neuralspace nlu create-project --help"
UPLOAD_DATASET_COMMAND = "neuralspace nlu upload-dataset --help"
INSTALL_APP_COMMAND = "neuralspace install-app --help"

# checking command

APP_IS_INSTALLED = "App is already installed"
