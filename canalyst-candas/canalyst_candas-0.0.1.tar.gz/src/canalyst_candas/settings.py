from pathlib import Path
from canalyst_candas.configuration.config import resolve_config, ConfigException
import json
import tempfile

DEFAULT_DIR = tempfile.gettempdir()
ROOT_DIR = Path().resolve()
MDS_HOST = "https://mds.canalyst.com"
WP_HOST = "https://app.canalyst.com"


def create_config():
    """
    Create configuration and set to CONFIG for Candas use
    """
    try:
        return resolve_config()
    except ConfigException:
        new_path = Path.home() / "canalyst"
        if not Path(new_path).exists():
            Path(new_path).mkdir()
        config_file = new_path / "keys.json"
        config_file_json = {
            "canalyst_api_key": "",
            "canalyst_s3_id": "",
            "canalyst_s3_key": "",
            "fred_key": "",
            "default_dir": "",
            "mds_host": "",
            "wp_host": "",
        }
        config_file.write_text(json.dumps(config_file_json))
        print(
            "Bad configuration. A configuration file has been created for you in \n"
            f"{config_file}. For Excel file downloads and scenario \n"
            "mapping, you'll need to add an API key to the 'canalyst_api_key' \n"
            "value. Visit https://app.canalyst.com/settings/api-tokens to create \n"
            "and retrieve your API key. You will also need to retrieve your \n"
            "S3 Access ID and Secret Key and fill in 'canalyst_s3_id' and \n"
            "'canalyst_s3_key' with those values, respectively. If using a \n"
            "Jupyter Notebook, stop and restart the notebook for the changes to \n"
            "take effect. If using a Python/iPython session, quit the current \n"
            "session and start a new one."
        )


CONFIG = create_config()
