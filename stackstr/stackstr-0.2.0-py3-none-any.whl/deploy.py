import logging
import json
from stackstr.common.utils import zip_util
from stackstr.common.api import upload_model
import zipfile
import torch
import joblib
import tempfile

SKLEARN = 'sklearn'
TF = 'tensorflow'
PYTORCH = 'pytorch'
KERAS = 'keras'

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def deploy(api_key, model, model_name):
    logger.info('gathering model metadata...')
    framework, _, _ = model.__class__.__module__.partition('.')

    if framework not in {SKLEARN, TF, KERAS}:
        if issubclass(model.__class__, torch.nn.Module):
            framework = PYTORCH

    if framework == SKLEARN:
        logger.info('packaging model...')
        model_object = _scikit_packager(model)
        logger.info('deploying model...')
        resp = upload_model(api_key, model_name, model_object, framework)
        model_object.close()
        if resp.status_code == 200:
            data = json.loads(resp.content)
            logger.info(f'model deployed at {data["model"]["url"]}')

    if framework == TF or framework == KERAS:
        logger.info('packaging model...')
        model_object = _tensorflow_packager(model)
        logger.info('deploying model...')
        resp = upload_model(api_key, model_name, model_object, framework)
        model_object.close()
        if resp.status_code == 200:
            data = json.loads(resp.content)
            logger.info(f'model deployed at {data["model"]["url"]}')

    if framework == PYTORCH:
        logger.info('packaging model...')
        model_object = _pytorch_packager(model)
        logger.info('deploying model...')
        resp = upload_model(api_key, model_name, model_object, framework)
        model_object.close()
        if resp.status_code == 200:
            data = json.loads(resp.content)
            logger.info(f'model deployed at {data["model"]["url"]}')

def _tensorflow_packager(model):
    temp_dir = tempfile.TemporaryDirectory()
    temp_file = tempfile.NamedTemporaryFile(suffix='.zip')
    model.save(temp_dir.name)
    zip = zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED)
    zip_util(temp_dir.name, zip)
    zip.close()
    temp_dir.cleanup()
    temp_file.file.seek(0)
    return temp_file

def _pytorch_packager(model):
    loaded_model = torch.jit.script(model)
    torch_model = tempfile.TemporaryFile(suffix='.pt')
    torch.jit.save(loaded_model, torch_model)
    torch_model.seek(0)
    return torch_model

def _scikit_packager(model):
    pickled_model = tempfile.TemporaryFile()
    joblib.dump(model, pickled_model, compress=True)
    pickled_model.seek(0)
    return pickled_model