#*****************************************************************#
# (C) Copyright IBM Corporation 2020.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#
'''Handle all config-based operations.
'''

import os
import re
import copy

from yaml.representer import SafeRepresenter
import yaml

class AttributeAccessDict(dict):
    '''Wrapper around Python dict to make it accessible like an object.
    '''
    def __init__(self, input_map):
        '''Recursively assign attribute access and call parent __init__ as well.

        Args:
            input_map:  dict
                Python dict which is to be assigned as attributes to self recursively and returned
                to the user to be able to be used via attribute-like access or Python dict-like.

        Returns:
            AttributeAccessDict
                Instance of class that allows for attribute-like access or Python dict-like, and
                overrides dict's methods to enable this. Can be modified later on and keep the same
                behavior.
        '''
        assert isinstance(input_map, dict), \
            '`input_map` argument should be of type dict, but found type: <{0}>'.format(
                type(input_map))

        # copy so as not to modify passed in dictionary
        copied_map = copy.deepcopy(input_map)

        # recursively instantiate sub-dicts
        for key, value in copied_map.items():
            copied_map[key] = AttributeAccessDict._make_attribute_access_dict(value)

        # make it accessible like native Python dict
        super().__init__(**copied_map)

    @staticmethod
    def _make_attribute_access_dict(value):
        if isinstance(value, AttributeAccessDict):
            return value
        elif isinstance(value, dict):
            return AttributeAccessDict(value)
        elif isinstance(value, list):
            return [AttributeAccessDict._make_attribute_access_dict(v) for v in value]
        else:
            return value

    # BELOW MAKES INSTANCE ACCESSIBLE VIA NATIVE PYTHON DICT METHODS ###############################

    def __getattr__(self, key, default=None):
        return super().get(key, default)

    def __setattr__(self, key, value):
        if isinstance(value, AttributeAccessDict):
            value = value
        elif isinstance(value, dict):
            value = AttributeAccessDict(value)
        super().__setitem__(key, value)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = AttributeAccessDict(value)
        super().__setitem__(key, value)

    def __delattr__(self, key):
        super().__delitem__(key)

    # ABOVE MAKES INSTANCE ACCESSIBLE VIA NATIVE PYTHON DICT METHODS ###############################

    def __deepcopy__(self, memo):
        '''This enables deepcopy to successfully copy a Config object, despite
        the default value semantics
        '''
        return AttributeAccessDict(copy.deepcopy(dict(self)))

class Config(AttributeAccessDict):
    '''Config which holds the configurations at the given config location.
    '''
    _search_pattern = re.compile('[.-]')

    def __init__(self, config, override_env_vars=True):
        '''

        NOTE:
            It is recommended NOT to use lists/arrays in .yaml files because lists cannot be
            inferred from environment variables.

        Args:
            config:  dict
                Config definition in a Python dictionary.
            override_env_vars:  bool
                If set to `False`, will NOT look for environment variables to override config with.

        Returns:
            Config
                Wrapped via internal methods so that it can be accessed using normal Python
                dictionary methods or nested attribute like syntax, for example:
                    `config.timeout.downstream_10`

        Note:
            Loaded Config will be available on `self` -- this class has no provided
            attributes in itself outside of the loaded config.
        '''
        # override with retrieved environment variable values if they exist
        updated_config = {key: value for key, value in config.items()}
        if override_env_vars:
            updated_config = self._update_with_env_vars(updated_config)

        # make it accessible like native Python dict and as attributes recursively; default == None
        super().__init__(updated_config)

    @classmethod
    def from_yaml(cls, config_location=None, **kwargs):
        '''Load a config definition at specified location, parse it, and get environment var's.

        Args:
            config_location:  str
                Should be of type: `*.yaml`, be parse-able, and be a valid file path. All files are
                assumed to be `utf8` encoded.
            **kwargs:  unpacked dict
                Passed along to `__init__`

        Returns:
            Config
                Wrapped via internal methods so that it can be accessed using normal Python
                dictionary methods or nested attribute like syntax, for example:
                    `config.timeout.downstream_10`
        '''
        # validate before moving forward: will raise exceptions if invalid
        config_location = cls._verify_config_location(config_location)

        loaded_config = cls._load_yaml_file(config_location)
        return cls(loaded_config, **kwargs)

    @staticmethod
    def _verify_config_location(config_location):
        '''Check to see if config location exists and is a .yaml file.
        NOTE: enforces .yaml extension.

        Args:
            config_location:  str
                Location of .yaml to parse where desired configurations exist.

        Returns:
            config_location:  bool
                Correct config_location relative to this file if the file exists and is .yaml file,
                otherwise raises AssertionError if config_location is not a Python str or if it is
                not a .yml/.yaml file or cannot be found.
        '''
        assert isinstance(config_location, str), \
            'config_location must be str, but you sent in type: <{0}>'.format(type(config_location))

        # cross-platform location relative to this file
        config_location = os.path.normpath(config_location)

        assert (config_location.endswith('.yml') or config_location.endswith('.yaml')), \
            'Must send in a .yaml or .yaml file'

        assert os.path.exists(config_location), \
            'config_location does not exist or cannot be found!'

        # finally found it's valid
        return config_location

    @staticmethod
    def _load_yaml_file(config_location):
        '''Helper to load .yaml file at location. Assumes file location has been validated.

        Args:
            config_location:  str
                Location of .yaml to parse where desired configurations exist.

        Returns:
            loaded_config:  dict
                Config definition in a Python dictionary.
        '''
        with open(config_location, 'r', encoding='utf8') as config_handle:
            loaded_config = yaml.safe_load(config_handle)

        # verify it is *definitely* a dict -- likely overkill
        return dict(loaded_config)

    @staticmethod
    def _eval_value(candidate_value):
        '''Logic to convert str version of given value into Python data type. Used for env. var's.

        Args:
            candidate_value:  str
                Value to be evaluated. Could be many malformed data types.

        Returns:
            converted_value:  bool, str, int, or float
                Value converted to its correct type. Leading/trailing whitespace stripped. If you
                did not pass in a Python str, throws TypeError.
        '''
        if not isinstance(candidate_value, str):
            raise TypeError(
                'Must pass in a str as candidate_value. You passed in type: <{0}>'.format(
                    type(candidate_value)))

        # try to get bool
        candidate_value = candidate_value.strip()

        if candidate_value.lower() == 'true':
            return True
        if candidate_value.lower() == 'false':
            return False

        # try to get an integer or a float
        try:
            float_val = float(candidate_value)
            if float_val.is_integer():
                try:
                    return int(candidate_value)
                except ValueError:
                    # not an actual int! should return float version -- is a 1.0 type value
                    pass
            # if it's not an integer, it's a float!
            return float_val
        except ValueError:
            pass
        # last chance -- return as string
        return str(candidate_value)

    def _update_with_env_vars(self, default_dict, prefix=None):
        '''Recursively update defaults with env. var's. Used for nested updating of dictionaries.

        Args:
            default_dict:  dict
                Python dict that holds the base/default values. To be updated with env. var's.

        Returns:
            updated_default_dict:  dict
                Same as default_dict where the default values are updated with env. var's
                if they were found and they are the same type.
        '''
        for default_key, default_val in default_dict.items():

            # step 1: Create the "full key" using the provided prefix
            if prefix:
                full_key = '.'.join([prefix, default_key])
            else:
                full_key = default_key

            # step 2: call recursively if necessary; skip empty dict's
            if isinstance(default_val, dict) and default_val:
                default_dict[default_key] = self._update_with_env_vars(default_val, full_key)

            # step 3: skip env. var. process for lists
            elif isinstance(default_val, list):
                continue

            # step 4: get environment variable key to look for
            env_var_key = self._env_var_from_key(full_key)

            # step 5: obtain the environment variable & convert to correct type if possible
            env_var_val = os.environ.get(env_var_key)
            if env_var_val is not None:
                env_var_val = self._eval_value(env_var_val)

                # step 5: update default_dict with value
                default_dict[default_key] = env_var_val

        # values have now been overriden where possible!
        return default_dict

    def _env_var_from_key(self, config_key):
        '''Convert a config key to the corresponding env var to check for.

        Args:
            config_key:  str
                Key in config file that should be converted to the environment variable to search
                for to override cofig_key's value with.

        Returns:
            env_var_key:  str
                Environment variable key to attempt to retrieve; converted from config_key.
                Replaced "." and "-" with "_" & upper-cased the key.
        '''

        return re.sub(self._search_pattern, '_', config_key.upper())


## yaml representation safe ########################################################################

yaml.add_representer(AttributeAccessDict, SafeRepresenter.represent_dict)
SafeRepresenter.add_representer(AttributeAccessDict, SafeRepresenter.represent_dict)
yaml.add_representer(Config, SafeRepresenter.represent_dict)
SafeRepresenter.add_representer(Config, SafeRepresenter.represent_dict)
