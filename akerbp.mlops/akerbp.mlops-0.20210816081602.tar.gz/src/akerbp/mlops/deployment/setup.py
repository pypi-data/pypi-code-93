#setup.py
from pathlib import Path

from akerbp.mlops import __version__ as version
from akerbp.mlops.core import logger 
from akerbp.mlops.deployment.helpers import to_folder, replace_string_file
from  akerbp.mlops.core.config import generate_default_project_settings
from  akerbp.mlops.core.config import validate_user_settings

logging=logger.get_logger(name='mlops_deployment')


def setup_pipeline(folder_path=Path('.'), overwrite=False):
    """
    Set up pipeline file in the given folder
    """
    pipeline_file = Path('bitbucket-pipelines.yml')
    pipeline_path = folder_path / pipeline_file
    if not overwrite and pipeline_path.exists():
        m = f"File {pipeline_file} exists already in folder '{folder_path}'"
        raise Exception(m)
    # Extract package resource
    pipeline = ('akerbp.mlops.deployment', pipeline_file)
    to_folder(pipeline, folder_path)
    # Set package version in the pipeline
    replace_string_file('MLOPS_VERSION', version, pipeline_path)


if __name__ == '__main__':
    logging.info("Create or overwrite pipeline file")
    setup_pipeline(overwrite=True) 
    if Path('mlops_settings.yaml').exists():
        logging.info("Validate settings file")
        validate_user_settings()
    else:
        logging.info("Create settings file template")
        generate_default_project_settings()
    logging.info("Done!")

