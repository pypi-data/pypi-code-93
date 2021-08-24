import json
import logging
import pathlib
import tempfile
import time
from typing import Dict, List, Union

import h5py
import numpy as np
import pandas as pd
import requests
import yaml

from baseten.common import api
from baseten.common.core import raises_api_error
from baseten.common.util import coerce_data_as_numpy_array

logger = logging.getLogger(__name__)

REQUIREMENTS_INSTALLATION_STATUS_RETRY_INTERVAL_SEC = 3
REQUIREMENTS_INSTALLATION_STATUS_MAX_TRIES = 20


def _build_h5_data_object(feature_data_np, target_data, metadata, data_temp_directory):
    data_temp_file = pathlib.PurePath(data_temp_directory, 'tmp.h5')
    data = {'features': feature_data_np}
    if np.any(target_data):
        data['targets'] = coerce_data_as_numpy_array(target_data)
    if np.any(metadata):
        data['metadata'] = json.dumps(metadata)

    h5_data = h5py.File(data_temp_file, mode='w')
    h5_sample_data_group = h5_data.create_group('sample_data')
    for key, np_obj in data.items():
        if key == 'metadata':
            dt = h5py.string_dtype(encoding='utf-8')
            h5_sample_data_group.create_dataset(key, data=np_obj, dtype=dt)
        else:
            h5_sample_data_group.create_dataset(key, data=np_obj)
    h5_data.close()
    return data_temp_file


@raises_api_error
def install_requirements(req_filepath: str):
    with open(req_filepath, 'r') as fp:
        requirements_txt = fp.read()
    logger.info(f'🚀 Sending requirements to BaseTen 🚀')
    resp = api.install_requirements(requirements_txt)
    status = resp['status']
    if status == 'PROCESSING':
        logger.info('🐳 Requirements are being installed 🐳')

        requirement_id = resp['id']
        tries = 0
        while tries < REQUIREMENTS_INSTALLATION_STATUS_MAX_TRIES:
            time.sleep(REQUIREMENTS_INSTALLATION_STATUS_RETRY_INTERVAL_SEC)
            resp = api.requirement_status(requirement_id)
            status = resp['status']
            if status != 'PROCESSING':
                break
            tries += 1
        else:
            logger.info('⌛ Requirements are still being installed. Check the status by running '
                        f'baseten.requirements_status(\'{requirement_id}\') ⌛')
    if status == 'SUCCEEDED':
        logger.info('🖖 Installed requirements successfully 🖖')
    elif status == 'FAILED':
        error_message = resp['error_message']
        logger.info(f'⚠️ Failed to install requirements. Error: "{error_message}" ⚠️')


@raises_api_error
def requirements_status(requirement_id: str):
    return api.requirement_status(requirement_id)


class BasetenDeployedModel:
    """A model backed by baseten serving. Provide either the model_id or the model_version_id."""
    def __init__(self, model_id: str = None,
                 model_version_id: str = None,
                 model_name: str = None):
        if not model_id and not model_version_id:
            raise ValueError('Either model_id or model_version_id must be provided.')

        if model_id and model_version_id:
            raise ValueError('Must provide either model_id or model_version_id; not both.')

        self._model_id = model_id
        self._model_version_id = model_version_id
        self._model_name = model_name
        self._model_config = None

    @property
    def model_version_id(self):
        return self._model_version_id

    @raises_api_error
    def predict(self,
                inputs: Union[List, pd.DataFrame, np.ndarray],
                metadata: Union[pd.DataFrame, List[Dict]] = None) -> List[List]:
        """Invokes the model given the input dataframe.

        Args:
            inputs: The data representing one or more inputs to call the model with.
                Accepted types are: list, pandas.DataFrame, and numpy.ndarray
            metadata (Union[pd.DataFrame, List[Dict]]): Metadata key/value pairs (e.g. name, url), one for each input.

        Returns:
            A list of inferences for each given input; e.g.: [[3], [9]] would indicate the prediction for the
            first input in inputs_df is [3], and the prediction for the second is [9].

        Raises:
            TypeError: If the provided inputs is not of a supported type.
            ApiError: If there was an error communicating with the server.
        """
        if isinstance(inputs, pd.DataFrame):
            inputs_list = inputs.to_dict('records')
        elif isinstance(inputs, (list, np.ndarray)):
            inputs_np_array = np.array(inputs)
            inputs_list = inputs_np_array.tolist()
        else:
            raise TypeError('predict can be called with either a list, a pandas DataFrame, or a numpy array.')

        if isinstance(metadata, pd.DataFrame):
            metadata = metadata.to_dict(orient='records')

        if self._model_version_id:
            return api.predict_for_model_version(self._model_version_id, inputs_list, metadata)
        return api.predict_for_model(self._model_id, inputs_list, metadata)

    @raises_api_error
    def update_model_config(self, model_config_file_path: str):
        """Update the model's feature names and output class labels (if any) based on the config
        found at `model_config_file_path`

        Args:
            model_config_file_path (str): The path to the model config file
        """
        config_yaml = yaml.safe_load(open(model_config_file_path, 'r'))
        feature_names = list(config_yaml['model_features']['features'])
        class_labels = config_yaml.get('model_class_labels', [])
        api.update_model_config(self._model_version_id, feature_names, class_labels)

    @raises_api_error
    def set_primary(self):
        """Promote this version of the model as the primary version.
        Raises:
            ApiError: If there was an error communicating with the server.
        """
        if not self._model_version_id:
            raise ValueError('Only a BasetenDeployedModel backed by a model_version can be set as primary.')
        return api.set_primary(self._model_version_id)

    @raises_api_error
    def upload_sample_data(self,
                           feature_data: Union[np.ndarray, pd.DataFrame, List[List]],
                           target_data: Union[np.ndarray, pd.DataFrame, List] = None,
                           metadata: List[Dict] = None,
                           data_name: str = 'validation_data',
                           ) -> Dict:
        """Upload a subset of the training/validation data to be used for
            - Summary statistics for the model
            - To detect model drift
            - To use as baseline data for model interpretability
            - To seed new data in the client.

        Training and validation data with targets must be uploaded with the targets separate.

        Args:
            feature_data (Union[np.ndarray, pd.DataFrame, List[List]]): The feature data to upload.
            target_data (Union[np.ndarray, pd.DataFrame, List[List]]): The target data to upload.
            metadata (List[Dict]): Metadata key/value pairs for the dataset.
            data_name (str): The name of the data set.

        Returns:
            Dict: The status of the upload.
        """

        feature_data_np = coerce_data_as_numpy_array(feature_data)

        signed_s3_upload_post = api.signed_s3_upload_post(self.model_version_id, data_name)
        logger.debug(f'Signed s3 upload post:\n{json.dumps(signed_s3_upload_post, indent=4)}')

        with tempfile.TemporaryDirectory() as data_temp_directory:
            data_temp_file = _build_h5_data_object(feature_data_np, target_data, metadata, data_temp_directory)
            files = {'file': (f'{data_name}.h5', open(data_temp_file, 'rb'))}
            form_fields = signed_s3_upload_post['form_fields']
            form_fields['AWSAccessKeyId'] = form_fields.pop('aws_access_key_id')
            s3_key = form_fields['key']
            requests.post(signed_s3_upload_post['url'], data=form_fields, files=files)
        return api.register_data_for_model(s3_key, self.model_version_id, data_name)
