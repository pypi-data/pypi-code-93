import configparser
import functools
import json
import logging
from typing import Dict, List

import requests

from baseten.common import settings
from baseten.common.core import ApiError, AuthorizationError
from baseten.common.util import base64_encoded_json_str

logger = logging.getLogger(__name__)


def with_api_key(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = settings.read_config()
        try:
            api_key = config.get('api', 'api_key')
        except configparser.NoOptionError:
            raise AuthorizationError('You must first run the `baseten login` cli command.')
        result = func(api_key, *args, **kwargs)
        return result
    return wrapper


@with_api_key
def models(api_key):
    query_string = '''
    {
      models {
        id,
        name
      }
    }
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']


@with_api_key
def create_model(api_key,
                 model_name,
                 s3_key,
                 model_framework,
                 model_type,
                 input_shape,
                 feature_names,
                 feature_summary,
                 class_labels,
                 model_framework_req,
                 semver_bump,
                 model_files_dict):
    encoded_input_shape = base64_encoded_json_str(input_shape)
    encoded_feature_names = base64_encoded_json_str(feature_names)
    encoded_feature_summary = base64_encoded_json_str(feature_summary)
    encoded_class_labels = base64_encoded_json_str(class_labels)
    encoded_model_framework_req = base64_encoded_json_str(model_framework_req)
    encoded_model_files_dict = base64_encoded_json_str(model_files_dict)
    if not model_name:
        import coolname
        model_name = coolname.generate_slug(2)
    query_string = f'''
    mutation {{
      create_model(name: "{model_name}"
                   s3_key: "{s3_key}",
                   model_framework: "{model_framework}",
                   model_type: "{model_type}",
                   semver_bump: "{semver_bump}",
                   encoded_input_shape: "{encoded_input_shape}",
                   encoded_feature_names: "{encoded_feature_names}",
                   encoded_feature_summary: "{encoded_feature_summary}",
                   encoded_class_labels: "{encoded_class_labels}",
                   encoded_model_framework_req: "{encoded_model_framework_req}"
                   encoded_model_files_dict: "{encoded_model_files_dict}"
      ) {{
        id,
        name,
        version_id
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model']


@ with_api_key
def models_versions(api_key, model_id):
    query_string = f'''
    {{
      model(id: "{model_id}") {{
        versions {{
          id,
          s3_key,
          feature_names,
          feature_summary
        }}
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model']


@ with_api_key
def model_version_input_shape(api_key, model_version_id):
    query_string = f'''
    {{
      model_version(id: "{model_version_id}") {{
        input_shape
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['model_version']['input_shape']


@ with_api_key
def create_model_version(api_key,
                         model_id,
                         s3_key,
                         model_framework,
                         model_type,
                         input_shape,
                         feature_names,
                         feature_summary,
                         class_labels,
                         model_framework_req,
                         semver_bump,
                         model_files_dict):
    encoded_input_shape = base64_encoded_json_str(input_shape)
    encoded_feature_names = base64_encoded_json_str(feature_names)
    encoded_feature_summary = base64_encoded_json_str(feature_summary)
    encoded_class_labels = base64_encoded_json_str(class_labels)
    encoded_model_framework_req = base64_encoded_json_str(model_framework_req)
    encoded_model_files_dict = base64_encoded_json_str(model_files_dict)
    query_string = f'''
    mutation {{
      create_model_version(model_id: "{model_id}",
                           s3_key: "{s3_key}",
                           model_framework: "{model_framework}",
                           model_type: "{model_type}",
                           semver_bump: "{semver_bump}",
                           encoded_input_shape: "{encoded_input_shape}",
                           encoded_feature_names: "{encoded_feature_names}",
                           encoded_feature_summary: "{encoded_feature_summary}",
                           encoded_class_labels: "{encoded_class_labels}",
                           encoded_model_framework_req: "{encoded_model_framework_req}"
                           encoded_model_files_dict: "{encoded_model_files_dict}") {{
        id,
        s3_key,
        feature_names,
        feature_summary
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_model_version']


@ with_api_key
def signed_s3_upload_post(api_key, model_file_name):
    query_string = f'''
    {{
      signed_s3_upload_url(model_file_name: "{model_file_name}") {{
        url,
        form_fields {{
          key,
          aws_access_key_id,
          policy,
          signature,
        }}
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['signed_s3_upload_url']


@ with_api_key
def register_data_for_model(api_key, s3_key, model_version_id, data_name):
    query_string = f'''
    mutation {{
        create_sample_data_file(model_version_id: "{model_version_id}",
                                name: "{data_name}",
                                s3_key: "{s3_key}") {{
          id
        }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_sample_data_file']


@with_api_key
def predict_for_model(api_key, model_id: str, inputs: list, metadata: List[Dict] = None) -> List[List]:
    """Call the model's predict given the input json.

    Args:
        api_key (str)
        model_id (str)
        inputs (list)
        metadata (List[Dict]): Metadata key/value pairs (e.g. name, url), one for each input.

    Raises:
        RequestException: If there was an error communicating with the server.
    """
    predict_url = f'{settings.API_URL_BASE}/models/{model_id}/predict'
    return _predict(api_key, predict_url, inputs, metadata)


@with_api_key
def predict_for_model_version(api_key, model_version_id: str, inputs: list, metadata: List[Dict] = None) -> List[List]:
    """Call the model version's predict given the input json.

    Args:
        api_key (str)
        model_version_id (str)
        inputs (list)
        metadata (List[Dict]): Metadata key/value pairs (e.g. name, url), one for each input.

    Raises:
        RequestException: If there was an error communicating with the server.
    """
    predict_url = f'{settings.API_URL_BASE}/model_versions/{model_version_id}/predict'
    return _predict(api_key, predict_url, inputs, metadata)


@with_api_key
def set_primary(api_key, model_version_id: str):
    """Promote this version of the model as the primary version.

    Args:
        api_key (str)
        model_version_id (str)
    """
    query_string = f'''
    mutation {{
      update_model_version(model_version_id: "{model_version_id}", is_primary: true) {{
        id,
        is_primary,
      }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['update_model_version']


@with_api_key
def update_model_config(api_key, model_version_id: str, feature_names: list, class_labels: list = None):
    """Update the feature names for the model.

    Args:
        api_key (str)
        model_version_id (str)
        feature_names (list)
        class_labels (Optional[list]): applies only to classifiers.
    """
    encoded_feature_names = base64_encoded_json_str(feature_names)
    encoded_class_labels = base64_encoded_json_str(class_labels)
    query_string = f'''
    mutation {{
      update_model_version(model_version_id: "{model_version_id}",
                           encoded_feature_names: "{encoded_feature_names}",
                           encoded_class_labels: "{encoded_class_labels}") {{
        id,
        feature_names,
      }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['update_model_version']


@with_api_key
def install_requirements(api_key, requirements_txt):
    escaped_requirements_txt = requirements_txt.replace('\n', '\\n')  # Otherwise the mutation becomes invalid graphql.
    query_string = f'''
    mutation {{
      create_pynode_requirement(requirements_txt: "{escaped_requirements_txt}") {{
        id
        status
        error_message
      }}
    }}
    '''
    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['create_pynode_requirement']


@with_api_key
def requirement_status(api_key, requirement_id):
    query_string = f'''
    {{
      pynode_requirement(id: "{requirement_id}") {{
        id
        status
        error_message
      }}
    }}
    '''

    resp = _post_graphql_query(api_key, query_string)
    return resp['data']['pynode_requirement']


def _predict(api_key, predict_url: str, inputs: list, metadata: List[Dict] = None) -> List[List]:
    resp = _post_rest_query(api_key, predict_url, {'inputs': inputs, 'metadata': metadata})
    resp_json = json.loads(resp.content)
    return resp_json['predictions']


def _headers(api_key):
    return {'Authorization': f'Api-Key {api_key}'}


def _post_graphql_query(api_key, query_string) -> dict:
    resp = requests.post(f'{settings.API_URL_BASE}/graphql/', data={'query': query_string}, headers=_headers(api_key))
    if not resp.ok:
        logger.error(f'GraphQL endpoint failed with error: {resp.content}')
        resp.raise_for_status()
    resp_dict = resp.json()
    errors = resp_dict.get('errors')
    if errors:
        raise ApiError(errors[0]['message'], resp)
    return resp_dict


def _post_rest_query(api_key, url, post_body_dict):
    resp = requests.post(url, json=post_body_dict, headers=_headers(api_key))
    resp.raise_for_status()
    return resp
