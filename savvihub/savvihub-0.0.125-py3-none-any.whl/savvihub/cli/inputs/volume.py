import os
from typing import List

from openapi_client import (
    ProtoVolumeMountRequest,
    ProtoVolumeMountRequestSourceDataset,
    ProtoVolumeMountRequestSourceDatasetVersion,
)
from savvihub.api.exceptions import NotFoundAPIException
from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context
from savvihub.cli.utils import parse_dataset
from savvihub.cli.constants import DATASET_VERSION_HASH_LATEST


def dataset_mount_callback(ctx: Context, dataset_mounts: List[str]) -> List[str]:
    client = ctx.authenticated_client
    organization_name = ctx.params['organization_name']
    ctx.store['dataset_mounts'] = []
    for dataset_mount in dataset_mounts:
        splitted = dataset_mount.split(':')
        if len(splitted) != 2:
            raise ExitException(f'Invalid dataset mount format: {dataset_mount}. '
                                f'You should specify both mount path and dataset name.\n'
                                f'ex) /input/dataset1:mnist@3d1e0f91c')

        mount_path, dataset_full_name = splitted
        mount_path = os.path.join(mount_path, '')  # Forcibly add slash to mount path
        organization_name_override, dataset_name, dataset_version_hash = parse_dataset(dataset_full_name)
        if organization_name_override:
            organization_name = organization_name_override

        dataset = client.dataset_read(organization_name, dataset_name)
        if dataset.is_version_enabled:
            if dataset_version_hash != DATASET_VERSION_HASH_LATEST:
                # Validate dataset version
                try:
                    dataset_version = client.dataset_version_read(dataset.id, dataset_version_hash)
                    dataset_version_hash = dataset_version.version_hash  # Replace with full version hash
                except NotFoundAPIException:
                    raise ExitException(f'Invalid dataset version: {dataset_full_name}\n'
                                        f'Please check your dataset version in `{organization_name}`.')
            ctx.store['dataset_mounts'].append(ProtoVolumeMountRequest(
                mount_type='dataset-version',
                mount_path=mount_path,
                dataset_version=ProtoVolumeMountRequestSourceDatasetVersion(
                    dataset_id=dataset.id,
                    dataset_name=dataset_name,
                    dataset_version_hash=dataset_version_hash,
                ),
            ))
        else:
            ctx.store['dataset_mounts'].append(ProtoVolumeMountRequest(
                mount_type='dataset',
                mount_path=mount_path,
                dataset=ProtoVolumeMountRequestSourceDataset(
                    dataset_id=dataset.id,
                    dataset_name=dataset_name,
                ),
            ))

    return dataset_mounts
