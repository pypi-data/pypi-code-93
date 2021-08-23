import os
import re
import yaml
import json
import glob
from pathlib import Path
import jinja2
from dsocli.logger import Logger
from dsocli.config import Configs
from dsocli.providers import Providers
from dsocli.templates import Templates, TemplateProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.exceptions import DSOException


_settings = {
    'templates_dir' : '{0}/templates'.format(Configs.config_dir),
}

_default_spec = {
}

def get_default_spec():
    return _default_spec.copy()


class LocalTemplateProvider(TemplateProvider):
    def __init__(self):
        super().__init__('template/local/v1')




    @property
    def templates_root_path(self):
        return f"{Configs.working_dir}/{_settings['templates_dir']}"



    def add(self, project, application, key, content):
        path = f"{self.templates_root_path}/{key}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        Logger.debug(f"Adding template: path={path}")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {
                'Key': key,
                'Path': os.path.join(_settings['templates_dir'], key),
            }



    def list(self, project, application, uninherited):
        #### local template provider does not support inheritancy
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.templates_root_path, encoding='utf-8'))
        templatesKeys = env.list_templates()
        result = []
        for key in templatesKeys:
            result.append({
                'Key': key, 
                'Path': os.path.join(_settings['templates_dir'], key),
                })
        return {'Templates': result}



    def get(self,  project, application, key, revision=None):
        path = f"{self.templates_root_path}/{key}"
        if not os.path.exists(path):
            raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}")
        Logger.debug(f"Getting template: path={path}")
        with open(path, 'r', encoding='utf-8') as f:
            result = f.read()
        return {
                'Key': key, 
                'Path': os.path.join(_settings['templates_dir'], key),
                'Contents': result
                }

# 

#     def delete(self, project, application, key, recursive=False):
#         result = []

#         path = f"{self.templates_root_path}/{key}"
#         path = re.sub('^./', '', path)

#         for item in glob.glob(path, recursive=recursive):
#             if not Path(item).is_file(): continue
#             Logger.debug(f"Deleting template: path={str(item)}")
#             os.remove(str(item))
#             key = str(item)[len(re.sub('^./', '', self.templates_root_path))+1:]
#             result.append({
#                     'Key': key, 
#                     'Path': os.path.join(_settings['templates_dir'], key)
#                     })
#         if not len(result):
#             raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}")
#         return result



    def delete(self, project, application, key):
        path = f"{self.templates_root_path}/{key}"
        if not os.path.exists(path) or os.path.isdir(path):
            raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}")
        Logger.debug(f"Deleting template: path={key}")
        os.remove(path)
        return {
                'Key': key, 
                'Path': path,
                }



    def history(self, project, application, key):
        raise DSOException('The template provider does not support versioning.')




Providers.register(LocalTemplateProvider())
