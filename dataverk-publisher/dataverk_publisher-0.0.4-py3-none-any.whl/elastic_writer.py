import logging
import os
from typing import Dict

from dataverk_publisher.connectors.elastic import ElasticSearchWriter
from dataverk_publisher.utils.environment import Environment


logger = logging.getLogger(__name__)


def write_es_index(datapackage_metadata: Dict):
    try:
        Environment(datapackage_metadata.get("environment"))
    except ValueError:
        logger.warning(
            f"""Invalid environment {datapackage_metadata.get("environment")}: Skipping writing to es index. 
            Valid environments are {[env.value for env in Environment]}"""
        )
    else:
        es_writer = ElasticSearchWriter(
            os.environ["DATAVERK_HOST"],
            datapackage_metadata,
            es_token=os.getenv("DATAVERK_ES_TOKEN"),
        )
        es_writer.write_metadata()
