import deetly

from typing import Any

from dataverk_publisher.elastic_writer import write_es_index
from dataverk_publisher.storage_writer import upload_resources
from dataverk_publisher.utils.environment import configure_environment


def publish_datapackage(datapackage: Any):

    if isinstance(datapackage, deetly.datapackage.Datapackage):
        datapackage.datapackage_metadata = datapackage.toJSON()

    configure_environment(datapackage.datapackage_metadata)

    write_es_index(datapackage.datapackage_metadata)
    upload_resources(datapackage)
