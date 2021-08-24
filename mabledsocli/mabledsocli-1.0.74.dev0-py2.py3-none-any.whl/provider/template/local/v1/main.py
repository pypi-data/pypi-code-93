import os
import re
from pathlib import Path
from mabledsocli.logger import Logger
from mabledsocli.config import Configs
from mabledsocli.providers import Providers
from mabledsocli.templates import TemplateProvider
from mabledsocli.stages import Stages
from mabledsocli.constants import *
from mabledsocli.exceptions import DSOException
from mabledsocli.contexts import Contexts
from mabledsocli.local_utils import *
from mabledsocli.settings import *


_default_spec = {
    'path': os.path.join(Configs.config_dir, 'templates')
}


def get_default_spec():
    return _default_spec.copy()


class LocalTemplateProvider(TemplateProvider):


    def __init__(self):
        super().__init__('template/local/v1')


    @property
    def template_root_dir(self):
        return Configs.template_spec('path')


    def get_prefix(self):
        return self.template_root_dir + os.sep


    def list(self, project, application, stage, uninherited=False, include_contents=False, filter=None):
        templates = load_context_resources(stage, prefix=self.get_prefix(), uninherited=uninherited, include_contents=include_contents, filter=filter)
        result = {'Templates': []}
        for key, details in templates.items():
            result['Templates'].append({
                                    'Key': key, 
                                    'Scope': details['Scope'],
                                    'Origin': details['Origin'],
                                    'Date': details['Date'],
                                    'Path': details['Path'],
                                    })

            if include_contents:
                result['Templates'][-1]['Contents'] = details['Contents']

        return result



    def add(self, project, application, stage, key, contents, render_path=None):
        if not Stages.is_default(stage) and not ALLOW_STAGE_TEMPLATES:
            raise DSOException(f"Templates may not be added to stage scopes, as the feature is currently disabled. It may be enabled by setting 'ALLOW_STAGE_TEMPLATES' to 'yes' in the DSO global settings.")
        
        path = get_local_path(stage, key, prefix=self.get_prefix())
        Logger.debug(f"Adding template: path={path}")
        fullPath = os.path.join(Configs.working_dir, path)
        os.makedirs(os.path.dirname(fullPath), exist_ok=True)
        with open(fullPath, 'w', encoding='utf-8') as f:
            f.write(contents)

        return {
                'Key': key,
                'Origin': {
                    'Project': project,
                    'Application': application,
                    'Stage': Stages.shorten(stage),
                },
                'Path': path,
            }


    def get(self, project, application, stage, key, revision=None):
        if revision:
            raise DSOException(f"Template provider '{Configs.template_provider}' does not support versioning.")

        Logger.debug(f"Locating template: project={project}, application={application}, stage={stage}, key={key}")
        found = locate_resource_in_context_hierachy(stage, key, prefix=self.get_prefix())
        if not found:
            raise DSOException(f"Template '{key}' not found nor inherited in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Getting template: path={key}")
        result = {
                'Key': key, 
                'Date': found[key]['Date'],
                'Scope': found[key]['Scope'],
                'Origin': found[key]['Origin'],
                'Path': found[key]['Path'],
                'Contents': found[key]['Contents'],
                }

        return result


    def delete(self, project, application, stage, key):
        Logger.debug(f"Locating template: project={project}, application={application}, stage={stage}, key={key}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_resource_in_context_hierachy(stage, key, prefix=self.get_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Deleting template: path={found[key]['Path']}")
        fullPath = os.path.join(Configs.working_dir, found[key]['Path'])
        os.remove(fullPath)
        return {
                'Key': key, 
                'Scope': found[key]['Scope'],
                'Origin': found[key]['Origin'],
                'Path': found[key]['Path'],
                }


    def history(self, project, application, stage, key, include_contents=False):
        raise DSOException(f"Template provider '{Configs.template_provider}' does not support versioning.")



def register():
    Providers.register(LocalTemplateProvider())
