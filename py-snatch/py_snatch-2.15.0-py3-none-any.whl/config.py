"""Get Environment Secrets for Snatch."""
import os
import sys
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from loguru import logger
from scalpl import Cut

from snatch.helpers.merge_dicts import merge_dicts
from snatch.helpers.secrets_manager import SecretManager

load_dotenv(verbose=True)


def get_environment_from_secrets_manager(
    environment: str, log_level: str
) -> Dict[Any, Any]:
    """Load settings from Secrets Manager..

    :return Dict[Any, Any]
    """
    env_name = os.getenv("ENV", "prd") if not environment else environment

    env_names = {
        "production": "prd",
        "staging": "stg",
        "develop": "dev",
        "local": "local",
        "dev": "dev",
        "stg": "stg",
        "prd": "prd",
    }
    current_env = env_names[env_name.strip().lower()]

    if "local" not in current_env:
        logger.remove()
        logger.add(sys.stderr, level=log_level)

    secrets = SecretManager(
        current_environment=current_env,
        project_name="snatch",
        current_env_data={},
    )

    secrets_manager_data = {"current_environment": current_env}
    if not secrets.can_read_secrets:
        logger.warning("Not reading Secrets Manager. Using local configuration...")
        return secrets_manager_data

    logger.info(
        f"Reading settings from `snatch/{current_env}` (logger level: {log_level})..."
    )

    secrets_manager_data.update(secrets.get_project_secrets())

    return secrets_manager_data


def get_datasource_url(name: str) -> str:
    env_name = f"SNATCH_{name.upper()}_URL"
    url = os.getenv(env_name)
    if url:
        logger.debug(f"Using value from {env_name}")
        return url
    return f"http://{name}"


def get_settings(environment: Optional[str], log_level: str):

    config = {
        "snatch": {
            "boa_vista_secret_token": os.getenv("SNATCH_BOA_VISTA_SECRET_TOKEN", "foo"),
            "datasource_boa_vista_url": get_datasource_url("datasource_boa_vista"),
            "banco_central_secret_token": os.getenv(
                "SNATCH_BANCO_CENTRAL_SECRET_TOKEN", "foo"
            ),
            "datasource_banco_central_url": get_datasource_url(
                "datasource_banco_central"
            ),
            "qsa_secret_token": os.getenv("SNATCH_QSA_SECRET_TOKEN", "foo"),
            "datasource_qsa_url": get_datasource_url("datasource_qsa"),
            "pep_secret_token": os.getenv("SNATCH_PEP_SECRET_TOKEN", "foo"),
            "datasource_pep_url": get_datasource_url("datasource_pep"),
            "rf_secret_token": os.getenv("SNATCH_RF_SECRET_TOKEN", "foo"),
            "datasource_rf_url": get_datasource_url("datasource_rf"),
            "ibama_secret_token": os.getenv("SNATCH_IBAMA_SECRET_TOKEN", "foo"),
            "datasource_ibama_url": get_datasource_url("datasource_ibama"),
            "data_risk_secret_token": os.getenv("SNATCH_DATA_RISK_SECRET_TOKEN", "foo"),
            "datasource_data_risk_url": get_datasource_url("datasource_data_risk"),
            "fgts_secret_token": os.getenv("SNATCH_FGTS_SECRET_TOKEN", "foo"),
            "datasource_fgts_url": get_datasource_url("datasource_fgts"),
            "protest_secret_token": os.getenv("SNATCH_PROTEST_SECRET_TOKEN", "foo"),
            "datasource_protest_url": get_datasource_url("datasource_protest"),
            "pgfn_secret_token": os.getenv("SNATCH_PGFN_SECRET_TOKEN", "foo"),
            "datasource_pgfn_url": get_datasource_url("datasource_pgfn"),
            "tst_secret_token": os.getenv("SNATCH_TST_SECRET_TOKEN", "foo"),
            "datasource_tst_url": get_datasource_url("datasource_tst"),
            "ceis_secret_token": os.getenv("SNATCH_CEIS_SECRET_TOKEN", "foo"),
            "datasource_ceis_url": get_datasource_url("datasource_ceis"),
            "cnep_secret_token": os.getenv("SNATCH_CNEP_SECRET_TOKEN", "foo"),
            "datasource_cnep_url": get_datasource_url("datasource_cnep"),
        }
    }
    data_from_secrets = get_environment_from_secrets_manager(
        environment=environment, log_level=log_level
    )

    merge_dicts(source_dict=data_from_secrets, target_dict=config)

    settings = Cut(config)
    return settings
