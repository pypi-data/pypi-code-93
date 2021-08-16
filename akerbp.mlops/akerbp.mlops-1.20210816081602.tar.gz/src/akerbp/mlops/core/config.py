# config.py
import os
import traceback
import re
from typing import List, Optional
from pydantic import FilePath
from pydantic.dataclasses import dataclass
from dataclasses import asdict
from pathlib import Path
import yaml

from akerbp.mlops.core import helpers 
from akerbp.mlops.core import logger

logging=logger.get_logger(name='mlops_core')


def validate_categorical(setting, name, allowed):
    if setting not in allowed:
        m = (f"{name}: allowed values are {allowed}, got '{setting}'")
        raise ValueError(m)


@dataclass
class EnvVar():
    env: Optional[str] = None
    service_name: Optional[str] = None
    google_project_id: Optional[str] = None
    platform: Optional[str] = None
    local_deployment: bool = False

    def __post_init__(self):        
        if self.env:
            validate_categorical(self.env, "Environment", ["dev", "test", "prod"])
        else:
            logging.warning("ENV environmental variable is not set")
        validate_categorical(self.platform, "Platform", ["cdf", "gc", None])
        if (self.env and self.env != 'dev'):
            validate_categorical(self.service_name, "Service  name", 
                ["training", "prediction"])


def _read_env_vars():
    """
    Read environmental variables and initialize EnvVar object with those that
    were set (i.e. ignored those with None value)
    """
    envs=dict(
        env=os.getenv('ENV'), 
        service_name=os.getenv('SERVICE_NAME'), 
        local_deployment=os.getenv('LOCAL_DEPLOYMENT'),
        google_project_id=os.getenv('GOOGLE_PROJECT_ID'),
        deployment_platform=os.getenv('DEPLOYMENT_PLATFORM'),
    )
    envs = {k:v for k,v in envs.items() if v}
    return EnvVar(**envs)

envs = _read_env_vars()
envs_dic=asdict(envs)
logging.debug(f"{envs_dic=}")

@dataclass
class CdfKeys():
    data: Optional[str]
    files: Optional[str]
    functions: Optional[str]

_api_keys = CdfKeys(
   data = os.getenv('COGNITE_API_KEY_DATA'),
   files = os.getenv('COGNITE_API_KEY_FILES'),
   functions = os.getenv('COGNITE_API_KEY_FUNCTIONS')
)
api_keys = asdict(_api_keys)

def update_cdf_keys(new_keys):
    global api_keys
    api_keys=asdict(CdfKeys(**new_keys))


def generate_default_project_settings(
    yaml_file=Path('mlops_settings.yaml'), 
    n_models=2
):
    if yaml_file.exists():
        raise Exception(f"Settings file {yaml_file} exists already.")
    
    default_config = [ 
"""
model_name: my_model
model_file: model_code/my_model.py
req_file: model_code/requirements.model
test_file: model_code/test_model.py
artifact_folder: artifact_folder
platform: cdf
info:
    prediction: 
        description: Description prediction service for my_model
        owner: datascientist@akerbp.com
    training:
        << : *desc
        description: Description training service for my_model
"""
    ]
    default_config *= n_models
    default_config = "---".join(default_config)
    with open(yaml_file, 'w') as f:
        f.write(default_config)


def validate_model_reqs(req_file):
    # Model reqs is renamed to requirements.txt during deployment
    if req_file.name == 'requirements.model':
        with req_file.open() as f: 
            req_file_string = f.read()
            if 'akerbp.mlops' not in req_file_string:
                m = 'Model requirements should include akerbp.mlops package'
                raise Exception(m)
            if 'MLOPS_VERSION' not in req_file_string:
                m = 'akerbp.mlops version should be "MLOPS_VERSION"'
                raise Exception(m)


@dataclass
class ServiceSettings():
    model_name: str # Remember to modify generate_default_project_settings()
    model_file: FilePath # if fields are modified
    req_file: FilePath
    test_file: Optional[FilePath]
    artifact_folder: Path
    info: dict
    platform: str = 'cdf'
    model_id: Optional[str] = None


    def __post_init_post_parse__(self):
        # Validation
        if not re.match("^[A-Za-z0-9_-]*$", self.model_name):
            raise Exception("Model name can only contain letters, numbers"
                            "underscores and dashes")

        validate_model_reqs(self.req_file)

        validate_categorical(self.platform, "Deployment platform", 
            ["cdf", "gc", "local"])

        if self.platform == 'gc' and not envs.google_project_id:
            raise Exception("Platform 'gc' requires GOOGLE_PROJECT_ID env var")

        if self.model_id and envs.service_name == 'training':
            raise ValueError("Unexpected model_id setting (training service)")
        
        # Derived fields
        if envs.env == 'dev' and not envs.local_deployment:
            self.platform = 'local'
        
        self.model_import_path = helpers.as_import_path(self.model_file)
        self.test_import_path = helpers.as_import_path(self.test_file)

        self.files = {
            "model code": helpers.get_top_folder(self.model_file), 
            "handler": ("akerbp.mlops.cdf", "handler.py"),
            "artifact folder": self.artifact_folder
        }
        if self.platform == "gc":
            files_gc = {
                "Dockerfile": ("akerbp.mlops.gc", "Dockerfile"),
                "requirements.app": ("akerbp.mlops.gc", "requirements.app"),
                "install_req_file.sh":("akerbp.mlops.gc", "install_req_file.sh")
            }
            self.files = {**self.files, **files_gc}


def store_service_settings(c, yaml_file=Path('mlops_service_settings.yaml')):
    logging.info("Write service settings file")

    def factory(data):
        """
        Take a list of tuples as input. Returns a suitable dictionary.
        Transforms Path objects to strings (linux style path).
        """
        path2str = lambda x: x if not isinstance(x,Path) else x.as_posix()
        d = {k:path2str(v) for k,v in data}
        return d
    
    service_settings=asdict(c, dict_factory=factory)
    with yaml_file.open('w') as f:
        yaml.dump(service_settings,f)


@dataclass
class ProjectSettings():
    project_settings: List[ServiceSettings]


def read_project_settings(yaml_file=Path('mlops_settings.yaml')):
    logging.info(f"Read project settings")
    with yaml_file.open() as f:
        settings = yaml.safe_load_all(f.read())
    model_settings = [ServiceSettings(**s) for s in settings]
    project_settings = ProjectSettings(project_settings=model_settings)
    logging.debug(f"{project_settings=}")        
    return project_settings.project_settings


def read_service_settings(yaml_file=Path('mlops_service_settings.yaml')):
    logging.info(f"Read service settings")
    with yaml_file.open() as f:
        settings = yaml.safe_load(f.read())
    service_settings = ServiceSettings(**settings)
    logging.debug(f"{service_settings=}")
    return service_settings


def validate_user_settings(yaml_file=Path('mlops_settings.yaml')):
    try:
        read_project_settings(yaml_file)
        logging.info("Settings file is ok :)")
    except Exception:
        trace = traceback.format_exc()
        error_message = f"Settings file is not ok! Fix this:\n{trace}"
        logging.error(error_message)
