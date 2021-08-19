import json
import os
from typing import Any

from dataverk_publisher.connectors.resources.dakan import DakanConnector
from dataverk_publisher.connectors.resources.local import FileStorageConnector
from dataverk_publisher.connectors.resources.google import GoogleStorageConnector
from dataverk_publisher.connectors.resources.base import StorageBase
from dataverk_publisher.utils.environment import Environment


def _get_storage_connector(environment: str) -> StorageBase:
    try:
        if Environment(environment) == Environment.NAIS:
            return DakanConnector(host=os.environ["DATAVERK_HOST"])
        else:
            return GoogleStorageConnector(bucket_name=os.environ["DATAVERK_BUCKET"])
    except ValueError:
        return FileStorageConnector()


def _write_metadata_file(storage_conn: StorageBase, datapackage: Any):
    storage_conn.write(
        file=json.dumps(datapackage.datapackage_metadata),
        dp_id=datapackage.datapackage_metadata["id"],
        resource_path="datapackage.json",
        fmt="json",
    )


def _write_resources(storage_conn: StorageBase, datapackage: Any):
    for resource in datapackage.resources:
        storage_conn.write(
            file=json.dumps(resource.get("data")) if isinstance(resource.get("data"), dict) else resource.get("data"),
            dp_id=datapackage.datapackage_metadata["id"],
            resource_path=resource.get("path"),
            fmt=resource.get("format"),
        )


def upload_resources(datapackage: Any):
    storage_conn = _get_storage_connector(
        datapackage.datapackage_metadata.get("environment")
    )
    _write_metadata_file(storage_conn, datapackage)
    _write_resources(storage_conn, datapackage)
