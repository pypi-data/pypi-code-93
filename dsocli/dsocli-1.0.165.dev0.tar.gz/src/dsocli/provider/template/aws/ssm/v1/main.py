import re
import boto3
from dsocli.exceptions import DSOException
from dsocli.logger import Logger
from dsocli.config import Configs
from dsocli.providers import Providers
from dsocli.templates import TemplateProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.dict_utils import set_dict_value
from dsocli.contexts import Contexts
from dsocli.aws_utils import *
from dsocli.settings import *

_default_spec = {
    'prefix': '/dso/v1/templates',
}

def get_default_spec():
    return _default_spec.copy()


_settings = {
    'id': 'template/aws/ssm/v1',
}


class AwsSsmTemplateProvider(TemplateProvider):

    ssm = None

    def __init__(self):
        super().__init__(_settings['id'])
        self.ssm = boto3.session.Session().client(service_name='ssm')



    def get_prefix(self):
        return Configs.template_spec('prefix')



    def list(self, project, application, stage, uninherited=False, include_contents=False, filter=None):
        templates = load_context_ssm_parameters(project, application, stage, 'StringList', prefix=self.get_prefix(), uninherited=uninherited)
        result = {'Templates': []}
        for key, details in templates.items():
            if filter and not re.match(filter, key): continue
            if include_contents:
                result['Templates'].append({
                                        'Key': key, 
                                        'Contents': details['Value'], 
                                        'Scope': details['Scope'],
                                        'Origin': details['Origin'],
                                        'RevisionId': str(details['Version']),
                                        'Date': details['Date'],
                                        'Path': details['Path'],
                                        })
            else:
                result['Templates'].append({
                                        'Key': key, 
                                        'Scope': details['Scope'],
                                        'Origin': details['Origin'],
                                        'RevisionId': str(details['Version']),
                                        'Date': details['Date'],
                                        'Path': details['Path'],
                                        })

        return result



    def add(self, project, application, stage, key, contents, render_path=None):
        if len(contents) > 4096:
            raise DSOException(f"This template provider does not support templates larger than 4KB.")
        if not Stages.is_default(stage) and not ALLOW_STAGE_TEMPLATES:
            raise DSOException(f"Templates may not be added to stage scopes, as the feature is currently disabled. It may be enabled by setting 'ALLOW_STAGE_TEMPLATES' to 'yes' in the DSO global settings.")
        Logger.debug(f"Checking SSM template overwrites: project={project}, application={application}, stage={stage}, key={key}")
        assert_ssm_parameter_no_namespace_overwrites(project, application, stage, key, prefix=self.get_prefix())
        Logger.debug(f"Locating SSM template: project={project}, application={application}, stage={stage}, key={key}")
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix(), uninherited=True)
        if found and not found['Type'] == 'StringList':
            raise DSOException(f"Failed to add template '{key}' becasue becasue the key is not available in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        path = get_ssm_path(project, application, stage=stage, key=key, prefix=self.get_prefix())
        Logger.info(f"Adding SSM template: path={path}")
        response = put_ssm_template(path, contents)
        return {
                'Key': key,
                'Scope': Contexts.translate_context(project, application, stage),
                'Origin': {
                    'Project': project,
                    'Application': application,
                    'Stage': Stages.shorten(stage),
                },
                'RevisionId': str(response['Version']),
                # 'Path': path,
            }



    def get(self, project, application, stage, key, revision=None):
        Logger.debug(f"Locating SSM template: project={project}, application={application}, stage={stage}, key={key}")
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix())
        if not found:
            raise DSOException(f"Template '{key}' not found nor inherited in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        else:
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Getting SSM template: path={found['Name']}")
        response = get_ssm_template_history(found['Name'])
        templates = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if revision is None:
            ### get the latest revision
            result = {
                    'RevisionId': str(templates[0]['Version']),
                    'Date': templates[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'User': templates[0]['LastModifiedUser'],
                    'Path': found['Name'],
                    'Contents': templates[0]['Value'],
                    }
        else:
            ### get specific revision
            templates = [x for x in templates if str(x['Version']) == revision]
            if not templates:
                raise DSOException(f"Revision '{revision}' not found for template '{key}' in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
            result = {
                    'RevisionId': str(templates[0]['Version']),
                    'Date': templates[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'User': templates[0]['LastModifiedUser'],
                    'Path': found['Name'],
                    'Contents': templates[0]['Value'],
                    }

        return result



    def history(self, project, application, stage, key, include_contents=False):
        Logger.debug(f"Locating SSM template: project={project}, application={application}, stage={stage}, key={key}")
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix())
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        else:
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Getting SSM template: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        parameters = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if include_contents:
            result = { "Revisions":
                [{
                    'RevisionId': str(template['Version']),
                    'Date': template['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    # 'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Origin': found['Origin'],
                    'User': template['LastModifiedUser'],
                    # 'Path': found['Name'],
                    'Contents': templates[0]['Value'],

                } for template in parameters]
            }
        else:
            result = { "Revisions":
                [{
                    'RevisionId': str(template['Version']),
                    'Date': template['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    # 'Key': key,
                    # 'Scope': found['Scope'],
                    # 'Origin': found['Origin'],
                    'User': template['LastModifiedUser'],
                    # 'Path': found['Name'],
                } for template in parameters]
            }

        return result



    def delete(self, project, application, stage, key):
        Logger.debug(f"Locating SSM template: project={project}, application={application}, stage={stage}, key={key}")
        ### only parameters owned by the stage can be deleted, hence uninherited=True
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        else:
            # if len(found) > 1:
            #     Logger.warn(f"More than one template found at '{found['Name']}'. The first one taken, and the rest were discarded.")
            if not found['Type'] == 'StringList':
                raise DSOException(f"Template '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Deleting SSM template: path={found['Name']}")
        delete_ssm_parameter(found['Name'])
        return {
                'Key': key, 
                'Scope': found['Scope'],
                'Origin': found['Origin'],
                # 'Path': found['Name'],
                }



def register():
    Providers.register(AwsSsmTemplateProvider())
