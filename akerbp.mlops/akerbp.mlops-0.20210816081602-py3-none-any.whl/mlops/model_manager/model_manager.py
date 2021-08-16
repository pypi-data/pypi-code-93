# model_manager.py

from pathlib import Path

import akerbp.mlops.cdf.helpers as cdf
from akerbp.mlops.core import config, logger
env = config.envs.env
logging=logger.get_logger(name='MLOps')


def setup(cdf_api_keys=None):
    """
    Set up the model manager. Currently this involves only setting up the CDF
    client. 
    
    Input:
        - cdf_api_keys: dictionary with cdf keys
    """
    if cdf_api_keys:
        cdf.api_keys = cdf_api_keys
    cdf.set_up_cdf_client()


def upload_new_model_version(model_name, env, folder, metadata={}):
    """
    Upload a new model version. Files in a folder are archived and stored 
    with external id `model_name/env/version`, where version is automatically
    increased. 

    Input:
        -model_name: name of the model 
        -env: name of the environment ('dev', 'test', 'prod')
        -folder: (Path) path to folder whose content will be uploaded
        -metadata: dictionary with metadata (it should not contain a 'version'
        key)
    
    Output:
        - model metadata (dictionary)
    """
    file_list = cdf.query_file_versions(
        external_id_prefix= f"{model_name}/{env}/", 
        directory_prefix='/mlops', 
        uploaded=None # count any file
    )
    if not file_list.empty:
        latest_v = file_list.metadata.apply(lambda d:int(d["version"])).max()
    else:
        latest_v = 0
    
    version = int(latest_v) + 1 # int64 isn't json-serializable
    if "version" in metadata:
        logging.error(
            "Metadata should not contain a 'version' key. "
            "It will be overwritten"
        )
    metadata["version"] = version
    external_id = f"{model_name}/{env}/{version}"

    if not isinstance(folder, Path):
        folder = Path(folder)
    
    folder_info = cdf.upload_folder(
        external_id, 
        folder, 
        metadata,
        target_folder='/mlops'
    )
    logging.info(f"Uploaded model with {external_id=} from {folder}")
    return folder_info


def find_model_version(model_name, env, metadata):
    """
    Model external id is specified by the model name and the environment
    (starts with `{model_name}/{env}`), and a query to the metadata. If this is
    not enough, the latest version is chosen.

    Input:
        -model_name: name of the model 
        -env: name of the environment ('dev', 'test', 'prod')
        -metadata: query to the metadata (dictionary), it can contain a
        'version' key
    """
    file_list = cdf.query_file_versions(
        directory_prefix='/mlops', 
        external_id_prefix=f"{model_name}/{env}",
        metadata=metadata
    )

    if (n_models := file_list.shape[0]) == 0:
        message = f"No model found with {model_name=} in {env=} and {metadata}"
        raise Exception(message)
    elif n_models > 1:
        logging.debug(f"Found {n_models} model files. Will choose the latest.")
    
    # Get latest in case there are more than one
    external_id = file_list.loc[file_list.uploadedTime.argmax(), "externalId"]
    return external_id


def download_model_version(model_name, env, folder, metadata={}):
    """
    Download a model version to a folder. First the model's external id is
    found, and then it is downloaded to the chosen folder (creating the folder
    if necessary).

    Input: 
        -model_name: name of the model 
        -env: name of the environment ('dev', 'test', 'prod')
        -folder: (Path) path to folder where the content will be uploaded
        -metadata: query to the metadata (dictionary)
    """
    external_id = find_model_version(model_name, env, metadata)
    if not folder.exists():
        folder.mkdir()
    cdf.download_folder(external_id, folder)
    logging.info(f"Downloaded model with {external_id=} to {folder}")
    return external_id


def set_up_model_artifact(artifact_folder, model_name):
    """
    Set up model artifacts. 
    When the prediction service is deployed, we need the model artifacts. These
    are downloaded, unless there's already a folder (local development
    environment only)
    
    Input:
      - artifact_folder (Path)
      - model_name
    
    Output:
      - model_id: either the model id provided by the model manager or a
        hardcoded value (existing folder in dev)
    """
    if artifact_folder.exists():
        if env=='dev':
            logging.info(f"Use model artifacts in {artifact_folder=}")
            model_id=f'{model_name}/dev/1'
            return model_id
        else:
            message = f"Existing artifacts won't be used ({env=})"
            logging.warning(message)
    
    logging.info("Download serialized model")
    model_id = download_model_version(model_name, env, artifact_folder)
    return model_id


def get_model_version_overview(model_name=None, env=None, metadata={}):
    """
    Get overview of model artifact versions. 

    Input:
        -model_name: name of the model or None for any
        -env: name of the environment ('dev', 'test', 'prod') or None for any
        -metadata: dictionary with metadata to query
    
    Output:
        - (dataframe) model artifact data (external id, id, etc.)
    """
    # All mlops files with right metadata
    file_list = cdf.query_file_versions(
        directory_prefix='/mlops', 
        external_id_prefix=None,
        uploaded=None,
        metadata=metadata
    )

    # query the external id
    if model_name:
        index = file_list.externalId.str.contains(model_name + "/")
        file_list = file_list.loc[index]
    if env:
        index = file_list.externalId.str.contains("/" + env + "/")
        file_list = file_list.loc[index]
    return file_list


def delete_model_version(external_id, confirm=True):
    """
    Delete a model artifact version

    Input:
        - external_id: (string) artifact's external id in CDF Files. 
            Model Manager builds external ids for the artifacts as follows: 
            "model_name/environment/version". This can be obtained from 
            the function `get_model_version_overview`
        - confirm: (bool) whether the user will be asked to confirm deletion
    """
    try:
        model, environment, version = external_id.split("/")
    except ValueError:
        logging.error(f"Expected external id format: 'name/env/version'")
        return

    confirmed = False

    file_list = cdf.query_file_versions(
        directory_prefix='/mlops', 
        external_id_prefix=external_id,
        uploaded=None
    )
    if file_list.empty:
        logging.error(f"File with '{external_id=}' not found")
        return

    if confirm:
        def confirm_prompt(question):
            reply = None
            while reply not in ("y", "n"):
                reply = input(f"{question} (y/n): ").lower()
            return (reply == "y")
        question = f"Delete {model=}, {environment=}, {version=}?"
        confirmed = confirm_prompt(question)

    if not confirm or confirmed:
        cdf.delete_file(dict(external_id=external_id))