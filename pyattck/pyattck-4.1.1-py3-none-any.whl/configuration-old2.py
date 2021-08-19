import os
import json
import warnings
from pathlib import Path
from urllib.parse import urlparse
import attr
import yaml
from requests.api import get, request
from .utils.exceptions import UknownFileError


def get_absolute_path(path_string: str) -> str:
    return os.path.abspath(
        os.path.expanduser(
            os.path.expandvars(path_string)
        )
    )

def set_value(value):
    return value

@attr.s
class Configuration:

    use_config            = attr.ib(default=False, type=bool)
    save_config           = attr.ib(default=False, type=bool)
    config_file_path      = attr.ib(default='~/pyattck/config.yml', type=str, converter=get_absolute_path)
    data_path             = attr.ib(default='~/pyattck/data', type=str, converter=get_absolute_path)
    enterprise_attck_json = attr.ib(default="https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json", type=str)
    pre_attck_json        = attr.ib(converter=set_value,default="https://raw.githubusercontent.com/mitre/cti/master/pre-attack/pre-attack.json", type=str)
    mobile_attck_json     = attr.ib(converter=set_value,default="https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json", type=str)
    nist_controls_json    = attr.ib(converter=set_value,default="https://raw.githubusercontent.com/center-for-threat-informed-defense/attack-control-framework-mappings/master/frameworks/nist800-53-r4/stix/nist800-53-r4-controls.json", type=str)
    generated_attck_json  = attr.ib(converter=set_value,default="https://github.com/swimlane/pyattck/blob/master/generated_attck_data.json?raw=True", type=str)
    generated_nist_json   = attr.ib(converter=set_value,default="https://github.com/swimlane/pyattck/blob/master/attck_to_nist_controls.json?raw=True", type=str)
    requests_kwargs       = attr.ib(default={})

    @config_file_path.validator
    def validate_config_file_path(cls, attribute, value):
        if value.endswith('.json') or value.endswith('.yml') or value.endswith('.yaml'):# or not cls.__check_if_path(value):
            pass
        else:
            raise ValueError('Please provide a config_file_path with .json, .yml, or .yaml extension.')

    @data_path.validator
    def validate_data_path(cls, attribute, value):
        if not cls.__check_if_path(value):
            raise ValueError('Please provide a directory for data_path value.')

    @enterprise_attck_json.validator
    @pre_attck_json.validator
    @mobile_attck_json.validator
    @nist_controls_json.validator
    @generated_attck_json.validator
    @generated_nist_json.validator
    def validate_path_or_url(cls, attribute, value):
        if not cls.__check_if_url(value) or not cls.__check_if_path(value):
            raise ValueError('Please provide a URl or path string as a value for any json files.')

    @classmethod
    def __get_absolute_path(cls, path_string):
        return os.path.abspath(
            os.path.expanduser(
                os.path.expandvars(path_string)
            )
        )

    @classmethod
    def __download_url_data(cls, url):
        return request('GET', url, **cls.requests_kwargs).json()

    @classmethod
    def __write_to_disk(cls, path, data):
        with open(path, 'w+') as file_obj:
            if path.endswith('.json'):
                json.dump(data, file_obj)
            elif path.endswith('.yml') or path.endswith('.yaml'):
                yaml.dump(data, file_obj)
            else:
                raise UknownFileError(provided_value=path, known_values=['.json', '.yml', '.yaml'])

    @classmethod
    def __check_if_path(cls, value):
        if Path(value):
            return True
        return False

    @classmethod
    def __check_if_url(cls, value):
        try:
            if urlparse(value).scheme in ['http', 'https']:
                return True
            return False
        except:
            return False

    @classmethod
    def __get_config(cls):
        config_dict = {}
        for key in attr.fields_dict(cls).keys():
            if hasattr(cls, key):
                if isinstance(getattr(cls, key), str) and not cls.__check_if_url(getattr(cls, key)):
                    config_dict[key] = cls.__get_absolute_path(getattr(cls, key))
                else:
                    config_dict[key] = getattr(cls, key)
        return config_dict

    @classmethod
    def get_config(cls):
        if not hasattr(Configuration, 'config_data'):
            Configuration.config_data = {}
        if not cls.config_data:
            print('here')
            if cls.save_config:
                cls.__save_data(cls.config_file_path, cls.__get_config())
                cls._save_json_data()
            if cls.use_config:
                cls.config_data = cls.__load_data(cls.config_file_path)
            else:
                cls.config_data = cls.__get_config()
        else:
            cls.config_data = cls.__get_config()
        return cls.config_data

    @classmethod
    def get_data(cls, value:str) -> dict:
        return cls.__load_data(cls.get_config().get(value))

    @classmethod
    def __load_data(cls, value):
        data = None
        if os.path.isfile(value):
            try:
                with open(value) as f:
                    if value.endswith('.json'):
                        data = json.load(f)
                    elif value.endswith('.yml') or value.endswith('.yaml'):
                        data = yaml.load(f, Loader=yaml.FullLoader)
                    else:
                        raise UknownFileError(provided_value=value, known_values=['.json', '.yml', '.yaml'])
            except:
                warnings.warn(f"Unable to load data from specified location: {value}")
        return data

    @classmethod
    def __save_data(cls, path, data):
        # save configuration to disk
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            except:
                raise Exception('pyattck attempted to create the provided directories but was unable to: {}'.format(path))
        cls.__write_to_disk(path, data)

    @classmethod
    def _save_json_data(cls, force: bool=False) -> None:
        if not os.path.exists(cls.data_path):
            try:
                os.makedirs(cls.data_path)
            except:
                raise Exception(
                    'Unable to save data to the provided location: {}'.format(cls.data_path)
                )
        for json_data in ['enterprise_attck_json', 'pre_attck_json', 
                          'mobile_attck_json', 'nist_controls_json', 
                          'generated_attck_json', 'generated_nist_json']:
            if cls.__check_if_url(getattr(cls, json_data)):
                path = cls.__get_absolute_path(os.path.join(cls.data_path, "{json_data}.json".format(json_data=json_data)))
                if not os.path.exists(path) or force:
                    data = cls.__download_url_data(getattr(cls, json_data))
                    cls.__write_to_disk(path, data)
                setattr(Configuration, json_data, path)
