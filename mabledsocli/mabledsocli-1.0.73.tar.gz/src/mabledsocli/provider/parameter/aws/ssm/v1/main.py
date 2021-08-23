import re
import boto3
from mabledsocli.exceptions import DSOException
from mabledsocli.logger import Logger
from mabledsocli.config import Configs
from mabledsocli.providers import Providers
from mabledsocli.parameters import ParameterProvider
from mabledsocli.stages import Stages
from mabledsocli.constants import *
from mabledsocli.dict_utils import set_dict_value
from mabledsocli.contexts import Contexts
from mabledsocli.aws_utils import *


_default_spec = {
    'prefix': '/dso/v1/parameters'
}

def get_default_spec():
    return _default_spec.copy()


_settings = {
    'id': 'parameter/aws/ssm/v1',
}


class AwsSsmParameterProvider(ParameterProvider):

    def __init__(self):
        super().__init__(_settings['id'])


    def get_prefix(self):
        return Configs.parameter_spec('prefix')


    def list(self, project, application, stage, uninherited=False, filter=None):
        parameters = load_context_ssm_parameters(project, application, stage, 'String', prefix=self.get_prefix(), uninherited=uninherited)
        result = {'Parameters': []}
        for key, details in parameters.items():
            if filter and not re.match(filter, key): continue
            result['Parameters'].append({
                                    'Key': key, 
                                    'Value': details['Value'], 
                                    'Scope': details['Scope'],
                                    'Origin': details['Origin'],
                                    'RevisionId': str(details['Version']),
                                    'Date': details['Date'],
                                    'Path': details['Path'],
                                    })

        return result



    def add(self, project, application, stage, key, value):
        Logger.debug(f"Checking SSM parameter overwrites: project={project}, application={application}, stage={stage}, key={key}")
        assert_ssm_parameter_no_namespace_overwrites(project, application, stage, key, prefix=self.get_prefix())
        Logger.debug(f"Locating SSM parameter: project={project}, application={application}, stage={stage}, key={key}")
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix(), uninherited=True)
        if found and not found['Type'] == 'String':
            raise DSOException(f"Failed to add parameter '{key}' becasue becasue the key is not available in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        path = get_ssm_path(project, application, stage=stage, key=key, prefix=self.get_prefix())
        Logger.info(f"Adding SSM parameter: path={path}")
        response = put_ssm_paramater(path, value)
        return {
                'Key': key, 
                'Value': value,
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
        Logger.debug(f"Locating SSM parameter: project={project}, application={application}, stage={stage}, key={key}")
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix())
        if not found:
            raise DSOException(f"Parameter '{key}' not found nor inherited in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        else:
            if not found['Type'] == 'String':
                raise DSOException(f"Parameter '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Getting SSM parameter: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        parameters = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        if revision is None:
            ### get the latest revision
            result = {
                    'RevisionId': str(parameters[0]['Version']),
                    'Date': parameters[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': parameters[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': parameters[0]['LastModifiedUser'],
                    }
        else:
            ### get specific revision
            parameters = [x for x in parameters if str(x['Version']) == revision]
            if not parameters:
                raise DSOException(f"Revision '{revision}' not found for parameter '{key}' in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
            result = {
                    'RevisionId':str(parameters[0]['Version']),
                    'Date': parameters[0]['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                    'Key': key, 
                    'Value': parameters[0]['Value'],
                    'Scope': found['Scope'],
                    'Origin': found['Origin'],
                    'Path': found['Name'],
                    'User': parameters[0]['LastModifiedUser'],
                    }

        return result



    def history(self, project, application, stage, key):
        Logger.debug(f"Locating SSM parameter: project={project}, application={application}, stage={stage}, key={key}")
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix())
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        else:
            if not found['Type'] == 'String':
                raise DSOException(f"Parameter '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Getting SSM parameter: path={found['Name']}")
        response = get_ssm_parameter_history(found['Name'])
        parameters = sorted(response['Parameters'], key=lambda x: int(x['Version']), reverse=True)
        result = { "Revisions":
            [{
                'RevisionId': str(parameter['Version']),
                'Date': parameter['LastModifiedDate'].strftime('%Y/%m/%d-%H:%M:%S'),
                # 'Key': key,
                'Value': parameter['Value'],
                # 'Scope': found['Scope'],
                # 'Origin': found['Origin'],
                'User': parameter['LastModifiedUser'],
                # 'Path': found['Name'],
            } for parameter in parameters]
        }

        return result



    def delete(self, project, application, stage, key):
        Logger.debug(f"Locating SSM parameter: project={project}, application={application}, stage={stage}, key={key}")
        ### only parameters owned by the context can be deleted, hence uninherited=True
        found = locate_ssm_parameter_in_context_hierachy(project, application, stage, key, prefix=self.get_prefix(), uninherited=True)
        if not found:
            raise DSOException(f"Parameter '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        else:
            # if len(found) > 1:
            #     Logger.warn(f"More than one parameter found at '{found['Name']}'. The first one taken, and the rest were discarded.")
            if not found['Type'] == 'String':
                raise DSOException(f"Parameter '{key}' not found in the given context: project={project}, application={application}, stage={Stages.shorten(stage)}")
        Logger.info(f"Deleting SSM parameter: path={found['Name']}")
        delete_ssm_parameter(found['Name'])
        return {
                'Key': key, 
                'Scope': found['Scope'],
                'Origin': found['Origin'],
                # 'Path': found['Name'],
                }



def register():
    Providers.register(AwsSsmParameterProvider())
