"""GitLab API RPC endpoints
"""
import json
import yaml

from .crud import APIBase

# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring


class GitLabCILintRPC(APIBase):

    def create(self, data: str) -> None:
        path = "/ci/lint"
        # de-serialise YAML content into python structures
        content = yaml.load(data, Loader=yaml.FullLoader)

        # Create the API structure so that content is a JSON serialised string.
        # This way, when this structure is serialised into JSON, content will be escaped
        data_dict = {
            "content": json.dumps(content)
        }

        # serialise python into a JSON string
        data_json = json.dumps(data_dict)

        # Sicne this class does not implement IGitLabAPICreate, it will pass the GitLab CI Yaml file in form of JSON to
        # the endpoint directly
        self.status = self._endpoint.create(path, data=data_json)
