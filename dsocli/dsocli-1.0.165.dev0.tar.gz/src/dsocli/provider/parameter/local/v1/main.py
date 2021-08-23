import os
import re
import yaml
import json
import pathlib
import numbers
from dsocli.logger import Logger
from dsocli.config import Configs
from dsocli.parameters import ParameterProvider
from dsocli.stages import Stages
from dsocli.constants import *
from dsocli.utils import *

defaults = {
    'format': 'yaml',
    'allowGroups': 'no',
    'prependGroups': 'yes',
    'groupDelimiter': '/',
    'nestedDelimiter': '.',
}

config = {
    'parameters_dir' : '{0}/parameters'.format(Configs.dir_name),
    'file_extension' : {
        'yaml' : 'yml',
        'json' : 'json',
    }
}

class LocalParameterProvider(ParameterProvider):

    def __init__(self):
        super().__init__('parameter/local/v1')




    def __get_param_file_extension(self):
        format = Configs.parameter_spec('format')
        if format is None:
            Logger.debug(f"'format' is not set for the parameter provider, defaulted to '{defaults['format']}'.")
            format = defaults['format']

        return config['file_extension'][format]



    def __get_params_root_path(self, context=None):
        if not context:
            return f"{Configs.working_dir}/{config['parameters_dir']}"
        stage, env = Stages.parse_context(context)
        # if env == 'default':
        #     return f"{params_root_path}/{stage}"
        # else:
        #     return f"{params_root_path}/{stage}/{env}"
        return f"{Configs.working_dir}/{config['parameters_dir']}/{stage}/{env}"



    def __parse_parameter_key(self, key):
        if '/' in key:
            keySplitted = key.split('/')
            name = keySplitted[-1]
            group = '/'.join(keySplitted[:-1])
        else:
            group = 'default_group'
            name = key

        return group, name



    def __get_param_group_from_key(self, key):
        return self.__parse_parameter_key(key)[0]



    def __get_param_name_from_key(self, key):
        return self.__parse_parameter_key(key)[1]



    def __parse_group_from_file_name(self, filename):
        return os.path.splitext(filename)[0]  ### get rid of extension



    def __get_param_file_name_from_key(self, key):
        fileName = self.__get_param_group_from_key(key)
        fileExt = self.__get_param_file_extension()
        return f"{fileName}.{fileExt}"




    def __get_param_file_path_from_key(self, context, key, create=False):
        root_path = self.__get_params_root_path(context)
        fileName = self.__get_param_file_name_from_key(key)
        filePath = f"{root_path}/{fileName}"
        if not os.path.exists(filePath):
            if create:
                pathlib.Path(os.path.dirname(filePath)).mkdir(parents=True, exist_ok=True) 
                open(filePath, 'w').close()
            else:
                return None
        return filePath



    def __load_param_file(self, path):
        fileExt = pathlib.Path(path).suffix
        if fileExt in ['.yml','.yaml']:
            return yaml.safe_load(open(path)) or {}
        elif fileExt in ['.json']:
            return json.load(open(path)) or {}



    def __save_param_file(self, data, path):
        fileExt = pathlib.Path(path).suffix
        if fileExt in ['.yml','.yaml']:
            with open(path, 'w') as outfile:
                yaml.dump(data, outfile, sort_keys=False, indent=2)
        else:
            with open(path, "w") as outfile: 
                json.dump(data, outfile, sort_keys=False, indent=2)



    def __list_param_file_names(self, path):
        result = []
        if os.path.exists(path):
            fileExt = self.__get_param_file_extension()
            for fileName in os.listdir(path):
                if fileName.endswith(fileExt):
                    result.append(fileName)        
        return result


 
    def __context_exists(self, context):
       return os.path.exists(self.__get_params_root_path(context))



    def __param_group_exists(self, context, key):
        return not self.__get_param_file_path_from_key(context, key) is None



    def __assert_param_file_exists(self, context, key):
        if context:
            if not self.__context_exists(context):
                # raise DSOException(CLI_MESSAGES['ContextNotFound'].format(context))
                raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key))

        if not self.__param_group_exists(context, key):
            # raise DSOException("Parameter group '{0}' not found.".format(self.__get_param_group_from_key(key)))
            raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key))



    def __load_param_file_from_key(self, context, key):
        paramFilePath = self.__get_param_file_path_from_key(context, key)
        if paramFilePath:
            return self.__load_param_file(paramFilePath)
        else:
            return None



    ### get inherited filepath
    def __locate_param_file_from_key(self, context, key):
        ### first check if overide param file exists in context
        path = self.__get_param_file_path_from_key(context, key)
        if not path and context:
            stage, env = Stages.parse_context(context)
            ### if not found, check default env in the stage
            if not env == 'defaut':
                path = self.__get_param_file_path_from_key(f"{stage}/default", key)
                ### if not found, check param root path
                if not path:
                    path = self.__get_param_file_path_from_key('', key)
        return path



    def add(self, context, key, value):
        paramFilePath = self.__get_param_file_path_from_key(context, key, create=True)
        params = self.__load_param_file(paramFilePath)
        paramName = self.__get_param_name_from_key(key)
        set_dict_value(params, paramName.split('.'), value)
        with open(paramFilePath, 'w') as configFile:
            yaml.dump(params, configFile, sort_keys=False, indent=2)



    def list(self, context, uninherited):

        # if not self.__context_exists(context):
        #     if uninherited:
        #         Logger.warn(CLI_MESSAGES['ContextNotFound'].format(context))
        #     else:
        #         Logger.warn(CLI_MESSAGES['ContextNotFoundListingInherited'].format(context))

        grouppedParameters = {}

        if uninherited:
            ### iterating through param files in root or stage/env and merge with paramDict
            path = self.__get_params_root_path(context)
            for fileName in self.__list_param_file_names(path):
                Logger.debug("Loading '{0}/{1}'".format(path, fileName))
                group = self.__parse_group_from_file_name(fileName)
                params = self.__load_param_file(os.path.join(path, fileName))
                grouppedParameters[group] = params

        ### if not uninherited:
        else:
            path = self.__get_params_root_path()
            ### iterating through parameters root files and add them to paramDict
            for fileName in self.__list_param_file_names(path):
                Logger.debug("Loading '{0}/{1}'".format(path, fileName))
                group = self.__parse_group_from_file_name(fileName)
                params = self.__load_param_file(os.path.join(path, fileName))
                if group in grouppedParameters.keys():
                    grouppedParameters[group] = merge_dicts(params, grouppedParameters[group])
                else:
                    grouppedParameters[group] = params

            if context: 
                stage, env = Stages.parse_context(context)
                
                ### iterating through param files in stage(/default) and add them to paramDict
                path = self.__get_params_root_path(f"{stage}/default")
                for fileName in self.__list_param_file_names(path):
                    Logger.debug("Loading '{0}/{1}'".format(path, fileName))
                    group = self.__parse_group_from_file_name(fileName)
                    params = self.__load_param_file(os.path.join(path, fileName))
                    if group in grouppedParameters.keys():
                        grouppedParameters[group] = merge_dicts(params, grouppedParameters[group])
                    else:
                        grouppedParameters[group] = params

                if not env == 'default':
                    ### iterating through param files in stage/env and merge them paramDict
                    path = self.__get_params_root_path(f"{stage}/{env}")
                    for fileName in self.__list_param_file_names(path):
                        Logger.debug("Loading '{0}/{1}'...".format(path, fileName))
                        group = self.__parse_group_from_file_name(fileName)
                        params = self.__load_param_file(os.path.join(path, fileName))
                        if group in grouppedParameters.keys():
                            grouppedParameters[group] = merge_dicts(params, grouppedParameters[group])
                        else:
                            grouppedParameters[group] = params

        prependGroups = Configs.parameter_spec('prependGroups')
        if prependGroups is None:
            Logger.debug(f"'prependGroups' is not set for the parameter provider, defaulted to '{defaults['prependGroups']}'.")
            prependGroups = defaults['prependGroups']

        groupDelimiter = Configs.parameter_spec('groupDelimiter') 
        if groupDelimiter is None:
            Logger.debug(f"'groupDelimiter' is not set for the parameter provider, defaulted to '{defaults['groupDelimiter']}'.")
            groupDelimiter = defaults['groupDelimiter']

        nestedDelimiter = Configs.parameter_spec('nestedDelimiter')
        if nestedDelimiter is None:
            Logger.debug(f"'nestedDelimiter' is not set for the parameter provider, defaulted to '{defaults['nestedDelimiter']}'.")
            nestedDelimiter = defaults['nestedDelimiter']

        # for group, params in grouppedParameters.items():
        #     for key, value in params.items():
        #         grouppedkey = f"{group}{groupDelimiter}{key}" if prependGroups and not group == 'default_group' else key
        #         if grouppedkey in parameters.keys():
        #             Logger.warn(f"'{group}/{key}' was ignored as it would duplicate '{grouppedkey}'.")
        #         set_dict_value(parameters, grouppedkey.split('.'), value)


        # if not nestedDelimiter == '.':
        #     parameters = flatten_dict(parameters, delimiter=nestedDelimiter)

        ### first flatten params, if only nestedDelimiter is not '.', otherwise jinja2 will ot be able to resolve dic nested items
        if not nestedDelimiter == '.':
            for group, params in grouppedParameters.items():
                grouppedParameters[group] = flatten_dict(params, delimiter=nestedDelimiter)

        parameters = {}
        for group, params in grouppedParameters.items():
            for key, value in params.items():
                grouppedkey = f"{group}{groupDelimiter}{key}" if prependGroups and not group == 'default_group' else key
                if grouppedkey in parameters.keys():
                    Logger.warn(f"'{group}/{key}' was ignored as it would duplicate '{grouppedkey}'.")
                set_dict_value(parameters, grouppedkey.split('.'), value)

        return parameters




    def get(self, context, key):
        path = self.__locate_param_file_from_key(context, key)
        if not path:
                raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key))
        params = self.__load_param_file(path)
        value = get_dict_item(params, self.__get_param_name_from_key(key).split('.'))
        if value is None or isinstance(value, dict):
            raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key))
        # if isinstance(value, dict):
        #     raise DSOException(CLI_MESSAGES['ParameterNotFoundScope'].format(key))
        return value



    def delete(self, context, key):
        self.__assert_param_file_exists(context, key)
        params = self.__load_param_file_from_key(context, key)
        keys = self.__get_param_name_from_key(key).split('.')
        if not del_dict_item(params, keys):
            raise DSOException(CLI_MESSAGES['ParameterNotFound'].format(key))
        ### recursively delet empty parent scopes 
        del_dict_empty_item(params, keys[:-1])
        path = self.__get_param_file_path_from_key(context, key)
        if len(params.keys()) > 0:
            self.__save_param_file(params, path)
        else:
            os.remove(path)
            conetxt_root_path = self.__get_params_root_path(context)
            if len(os.listdir(conetxt_root_path)) == 0:
                os.rmdir(conetxt_root_path)


