import dataclasses
import uuid

from aide_sdk.manifests.manifest import load, set_manifest

global_context = None


def get_execution_context(manifest=None):
    global global_context
    if not global_context:
        start_new_execution(manifest)
    return global_context


def start_new_execution(manifest=None):
    if manifest:
        # Set the manifest to be the new global manifest
        set_manifest(manifest)

    manifest = load()

    global global_context
    global_context = ExecutionContext(execution_uid=uuid.uuid4(),
                                      model_name=manifest.model_name,
                                      model_version=manifest.model_version,
                                      model_uid=manifest.model_uid,
                                      mode=manifest.mode)
    return global_context


@dataclasses.dataclass
class ExecutionContext:
    execution_uid: uuid.UUID
    model_uid: str
    model_name: str = None
    model_version: str = None
    mode: str = None
    clinical_review_received: bool = None
