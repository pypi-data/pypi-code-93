
import re
from .constants import *
from .exceptions import DSOException
from .config import Configs
from .stages import Stages

class ContextUtils():

    contexts_translation_matrix = {
        'default': {
            'default': {
                'default': {
                    '0': "Global",
                },
                'stage': {
                    '0': "Global Stage",
                    'n': "Global Numbered Stage",
                },
            },
        },
        'project': {
            'default': {
                'default': {
                    '0': "Project",
                },
                'stage': {
                    '0': "Project Stage",
                    'n': "Project Numbered Stage",
                },
            },
            'application': {
                'default': {
                    '0': "Application",
                },
                'stage': {
                    '0': "Application Stage",
                    'n': "Application Numbered Stage",
                },
            },
        },
    }



    def translate_context(self, project, application, stage):
        stage = Stages.normalize(stage)
        project_idx = 'default' if project == 'default' else 'project'
        application_idx = 'default' if application =='default' else 'application'
        stage_idx = 'default' if Stages.is_default(stage) else 'stage'
        n_idx = '0' if Stages.is_default_env(stage) else 'n'
        return self.contexts_translation_matrix[project_idx][application_idx][stage_idx][n_idx]



    def encode_context_path(self, project, application, stage, key=None):
        result = f"/{project}"
        ### every application must belong to a project, no application overrides allowed in the default project
        if not project == 'default':
            result += f"/{application}"
        else:
            result += "/default"
        stage = Stages.normalize(stage)
        result += f"/{stage}"
        if key:
            result += f"/{key}"
        return result



    def decode_context_path(self, path):
        """
            path is in the form of [/]project/application/stage/env_no/[key]
        """
        parts = path.split('/')
        if not parts[0]: parts.pop(0)
        project = parts[0]
        application = parts[1]
        stage = f"{parts[2]}/{parts[3]}"
        if len(parts) > 4:
            key = parts[4:]
            return project, application, stage, key
        else:
            return project, application, stage




    def get_hierachy_context_paths(self, project, application, stage, key, prefix='', allow_stages=True, uninherited=False):
        
        result = []
        if uninherited:
            result.append(prefix + self.encode_context_path(project, application, stage, key))
        else:
            ### Add the global context: /default/default/default/0
            result.append(prefix + self.encode_context_path('default', 'default', 'default/0', key))
            if allow_stages and not Stages.is_default(stage):
                ### Add global stage context
                result.append(prefix + self.encode_context_path('default', 'default', Stages.get_default_env(stage), key))
                ### Add global numbered stage context
                if not Stages.is_default_env(stage):
                    result.append(prefix + self.encode_context_path('default', 'default', stage, key))

            if not project == 'default':
                ### Add the project context: /project/default/default/0
                result.append(prefix + self.encode_context_path(project, 'default', 'default/0', key))
                if allow_stages and not Stages.is_default(stage):
                    ### Add the project stage context: /project/default/stage/0
                    result.append(prefix + self.encode_context_path(project, 'default', Stages.get_default_env(stage), key))
                    ### Add the project numbered stage context: /project/default/stage/env
                    if not Stages.is_default_env(stage):
                        result.append(prefix + self.encode_context_path(project, 'default', stage, key))
                
                if not application == 'default':
                    ### Add the application context: /project/application/default/0
                    result.append(prefix + self.encode_context_path(project, application, 'default/0', key))
                    if  allow_stages and not Stages.is_default(stage):
                        ### Add the project stage context: /project/application/stage/0
                        result.append(prefix + self.encode_context_path(project, application, Stages.get_default_env(stage), key))
                        ### Add the application numbered stage context: /dso/project/application/stage/env
                        if not Stages.is_default_env(stage):
                            result.append(prefix + self.encode_context_path(project, application, stage, key))

        return result
        

Contexts = ContextUtils()