# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import requests
import shutil
import tempfile
from pathlib import Path
from io import BytesIO

from azure.ml.component._util._utils import _extract_zip
from azure.ml.component._util._loggerfactory import _LoggerFactory, track
from .._core._component_definition import ComponentType
from .._restclients.service_caller_factory import _DesignerServiceCallerFactory
from ._component_snapshot_cache import ComponentSnapshotCache
from ._constants import MOCK_PARALLEL_DRIVER, RUN_PREPARE_LOG


max_cache_snapshot = 50
max_unused_time = 1000 * 60 * 60 * 6
snapshot_cache_dir = os.path.join(tempfile.gettempdir(), 'azureml_snapshot_cache')
snapshot_cache = ComponentSnapshotCache(snapshot_cache_dir, max_cache_snapshot, max_unused_time)
_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


def _get_snapshot_content(component):
    service_caller = _DesignerServiceCallerFactory.get_instance(component.workspace)
    snapshot_url = service_caller.get_module_snapshot_url_by_id(module_id=component._identifier)
    response = requests.get(snapshot_url, allow_redirects=True)
    return response.content


@track(_get_logger)
def _prepare_component_snapshot(component, target_dir):
    """
    Get component snapshot and move to target_dir. If snapshot exists in cache, will copy it to target_dir.
    If not, will download snapshot to target_dir.

    :param component: component to get snapshot
    :type component: azure.ml.component.Component
    :param target_dir: snapshot store path
    :type target_dir: str
    """
    # Currently this function only works for the registered component which has an identifier,
    # however, a component could be directly loaded from a local directory without a registered identifier,
    # so we need to have different logic according to "component_id".
    # TODO: Refine the logic and put the cache related logic into _definition.get_snapshot
    # Get snapshot dir from cache
    component_id = component._identifier
    if component_id and snapshot_cache.prepare_snapshot_from_cache(component_id, target_dir):
        return
    print('{}: download {} snapshot...'.format(RUN_PREPARE_LOG, component.name))

    # If snapshot not exists in cache, download snapshot
    component._definition.get_snapshot(target=target_dir, overwrite=True)

    if component.type == ComponentType.ParallelComponent.value:
        _mock_parallel_driver_file(target_dir)

    # Add snapshot to snapshot cache dir
    if component_id:
        snapshot_cache.cache_snapshot(component_id, target_dir)
    print('{}: download {} snapshot completed...'.format(RUN_PREPARE_LOG, component.name))


def _download_snapshot(snapshot_url, script_path):
    # download snapshot to target directory
    response = requests.get(snapshot_url, allow_redirects=True)
    # extract snapshot to script path
    _extract_zip(BytesIO(response.content), script_path)


def _mock_parallel_driver_file(target_dir):
    # For parallel component, we use a mock driver to run the component.
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    target_entry = Path(target_dir) / MOCK_PARALLEL_DRIVER
    if target_entry.exists():
        target_entry.unlink()
    src_entry = Path(__file__).parent / MOCK_PARALLEL_DRIVER
    shutil.copyfile(str(src_entry), str(target_entry))
