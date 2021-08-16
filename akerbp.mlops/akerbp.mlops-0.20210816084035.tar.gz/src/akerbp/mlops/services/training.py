"""
service.py

Training service
"""
from tempfile import TemporaryDirectory
from importlib import import_module

import akerbp.mlops.model_manager as mm
from akerbp.mlops import __version__ as version
from akerbp.mlops.core import config, logger 
logging=logger.get_logger("mlops_services")
c = config.read_service_settings()
env = config.envs.env

model_module = import_module(c.model_import_path)
train = model_module.train
ModelException = model_module.ModelException

logging.debug(f"MLOps framework version {version}")


def _saver(path, metadata, cdf_api_keys):
    """
    Upload model folder to CDF Files
    """
    mm.setup(cdf_api_keys)
    model_info = mm.upload_new_model_version(
        c.model_name, 
        env,  
        path,
        metadata
    )
    return model_info


def service(data, secrets, saver=_saver):
    """
    Training service
    Inputs:
        - data: dictionary, data passed by the user through the API
        - secrets: dictionary with api keys
        - saver: an object that saves the model folder

    Output:
        - Dictionary with status 'ok' or 'error' as keys.
            status == 'ok'    -> there is a 'training' key as well  
                                (data on the model file)
            status == 'error' -> there is a 'message' key as well
    """
    try:
        with TemporaryDirectory() as temp_dir:
            metadata = train(data=data, folder_path=temp_dir, secrets=secrets)
            logging.debug(f"{metadata=}")
            model_info = saver(temp_dir, metadata, secrets)
        return dict(status="ok", training=model_info)
    except ModelException as e:
        error_message = f"Training failed. Message: {e}"
        logging.error(error_message)
        return dict(status='error', message=error_message)
        
        
    
