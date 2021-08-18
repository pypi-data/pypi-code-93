import os
import sys

import toml
from jsonschema import validate, ValidationError

from savvihub.cli.constants import DEFAULT_CONFIG_PATH


class ConfigLoader:
    def __init__(self, filename, schema):
        self.filename = filename
        self.schema = schema
        try:
            self.data = self._load()
        except toml.decoder.TomlDecodeError as e:
            print(f"fatal: bad config line {e.lineno} in file {filename}")
            sys.exit(1)

        self._validate()

    def _load(self):
        try:
            with open(self.filename) as f:
                documents = toml.load(f)
                if not documents:
                    return None
                data_dict = dict()
                for item, doc in documents.items():
                    data_dict[item] = doc
                return data_dict
        except FileNotFoundError:
            return {}

    def _validate(self):
        try:
            validate(instance=self.data, schema=self.schema)
        except ValidationError as e:
            return e.schema["Validation Error"]

    def save(self):
        self._validate()
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        try:
            with open(self.filename, 'w') as f:
                toml.dump(self.data, f)
        except EnvironmentError:
            print('Error: Config file not found')


class GlobalConfigLoader(ConfigLoader):
    schema = {
        "anyOf": [
            {},
            {
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "properties": {
                            "organization": {"type": "string"},
                            "token": {"type": "string"},
                            "workspace": {"type": "integer"},
                        },
                    },
                }
            },
        ]
    }

    def __init__(self):
        super().__init__(DEFAULT_CONFIG_PATH, self.schema)

    @property
    def token(self):
        return self.data.get('user', {}).get('token')

    @token.setter
    def token(self, token):
        user = self.data.get('user', {})
        if token:
            user['token'] = token
        self.data['user'] = user
        self.save()

    @property
    def organization(self):
        return self.data.get('user', {}).get('organization')

    @organization.setter
    def organization(self, organization_name):
        user = self.data.get('user', {})
        if organization_name:
            user['organization'] = organization_name
        self.data['user'] = user
        self.save()

    @property
    def workspace(self):
        return self.data.get('user', {}).get('workspace')

    @workspace.setter
    def workspace(self, workspace_slug):
        user = self.data.get('user', {})
        if workspace_slug:
            user['workspace'] = workspace_slug
        self.data['user'] = user
        self.save()
