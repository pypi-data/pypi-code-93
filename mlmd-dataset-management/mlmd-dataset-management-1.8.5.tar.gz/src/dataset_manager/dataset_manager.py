from multiprocessing import Array
from dataset_management.blob import get_bucket_name
from mlmd.dataset_manager_dao import create_artifact, create_context, get_artifact_by_type_and_name, get_artifacts_by_type, create_association_attribution, get_context
from mlmd.dataset_manager_scheme import ContextType, ArtifactType
from dataset_management.dataset import Dataset
from dataset_management.utils import generate_version_id
from google.cloud import storage
import datetime
import os

username = os.environ.get("DATASET_MANAGEMENT_USERNAME")
if username is None:
    raise Exception("No username found. please config your username in env DATASET_MANAGEMENT_USERNAME")

def _is_tag_hit(requested_tags, tags):
    if requested_tags is None or requested_tags == '':
        return True
    if tags is None or tags == '':
        return False
    for tag in requested_tags:
        if tag in tags:
            return True
    return False

def list_datasets(tags:Array=None):
    return [{
        "name": dataset.name,
        "created_at": datetime.datetime.fromtimestamp(dataset.create_time_since_epoch//1000.0).strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": dataset.properties["created_by"].string_value,
        "latest_version": dataset.properties["latest_version"].string_value,
        "tags": dataset.properties["tags"].string_value,
        } for dataset in get_artifacts_by_type(ArtifactType.DATASET) if _is_tag_hit(tags, dataset.properties["tags"].string_value.split(","))]

def get_dataset(name, version="latest"):
    global username
    ds = Dataset(name, version)
    return ds

def create_dataset(name, get_if_exists=False):
    dataset = get_artifact_by_type_and_name(ArtifactType.DATASET, name)
    if dataset is not None:
        if get_if_exists:
            return get_dataset(name)
        else:
            raise Exception("Dataset {} existed".format(name))
    
    # mlmd
    global username
    uncommitted_version_id = generate_version_id()
    context_id = create_context(ContextType.COMMIT_DATASET_VERSION, uncommitted_version_id, None, None)
    artifact_id = create_artifact(ArtifactType.DATASET, {"name": name, "created_by": username, "uncommitted_version": uncommitted_version_id})
    create_association_attribution(context_id, None, artifact_id)

    # bucket link
    storage_client = storage.Client()
    bucket = storage_client.bucket(get_bucket_name(name))
    if bucket.exists():
        print("WARNING: Bucket {} existed".format(name))
    else:
        bucket.storage_class = "STANDARD"
        storage_client.create_bucket(bucket, location="eu")

    return Dataset(name)

def delete_dataset(name):
    print("Not yet implemeted")
    pass
