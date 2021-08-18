import hashlib
import json
from typing import Iterator, List, Tuple

from cognite.client.data_classes import Asset
from cognite.experimental import CogniteClient

from cognite.airworkflow.util.cdf import data_set_id

from .scheduling import (
    Schedule,
    create_schedule_instance,
    create_schedules,
    retrieve_model_assets,
    retrieve_schedule_assets,
    retrieve_updated_schedules,
    update_schedules,
)

AIR_INFRA = "airInfra"
MODEL_POSTFIX = ":latest"
DATA_SET_NAME = "AIR"
EXCLUDED = ["loadbalancer"]


def retrieve_infra_model_assets(client) -> Iterator[Asset]:
    assets = retrieve_model_assets(client, [AIR_INFRA])
    assets = filter(lambda x: x.metadata.get("schedule") and x.external_id not in EXCLUDED, assets)
    return assets


def retrieve_schedule_asset_without_asset(client: CogniteClient) -> List:
    air_assets: List[Asset] = client.assets.list(data_set_ids=[data_set_id(client, DATA_SET_NAME)], limit=-1)
    assets: Iterator[Asset] = retrieve_infra_model_assets(client)
    assets_to_create: List[Asset] = []
    for asset in assets:
        if not any([asset.external_id == x.parent_external_id and "schedule" in x.name for x in air_assets]):
            assets_to_create.append(asset)
    return assets_to_create


def create_asset(client, asset: Asset) -> str:
    data = json.dumps({})
    hashed = hashlib.md5(f"{asset.external_id}-{data}".encode()).hexdigest()  # nosec
    asset_to_create = Asset(
        data_set_id=data_set_id(client, DATA_SET_NAME),
        name=f"{asset.name} schedule",
        external_id=hashed,
        parent_external_id=asset.external_id,
        metadata={"data": data},
    )
    if client.assets.retrieve(external_id=hashed) is None:
        client.assets.create(asset_to_create)
    return hashed


def retrieve_undeployed_infra_schedule_assets(
    client: CogniteClient,
) -> List[Schedule]:
    schedule_assets = retrieve_schedule_assets(client)
    schedules = client.functions.schedules.list()
    schedules_external_ids = map(lambda s: s.description, schedules)
    undeployed_schedule_assets = [i for i in schedule_assets if i.external_id not in schedules_external_ids]
    infra_schedule_assets = list(retrieve_infra_model_assets(client))
    undeployed_infra = filter(
        lambda u: u.parent_external_id in map(lambda a: a.name, infra_schedule_assets),
        undeployed_schedule_assets,
    )
    undeployed_infra_schedules: List[Schedule] = []
    for i in undeployed_infra:
        undeployed_infra_schedules += create_schedule_instance(client, i.external_id)
    return undeployed_infra_schedules


def retrieve_updated_infra_schedules(client: CogniteClient) -> Tuple:
    infra_assets = list(retrieve_infra_model_assets(client))
    updated, to_be_deleted = retrieve_updated_schedules(client)
    updated_filtered = filter(
        lambda x: x.model in map(lambda i: i.external_id, infra_assets),
        updated,
    )
    to_be_deleted_filtered = filter(
        lambda x: x.model in map(lambda i: i.external_id, infra_assets),
        to_be_deleted,
    )
    return list(updated_filtered), list(to_be_deleted_filtered)


def delete_double_schedules(client: CogniteClient, model_names: List):
    schedules = client.functions.schedules.list()
    for model_name in model_names:
        model_schedules = list(filter(lambda s: model_name in s.function_external_id, schedules))
        unique_schedules = set(map(lambda s: s.name, model_schedules))
        for i in unique_schedules:
            extracted = list(filter(lambda s: s.name == i, model_schedules))
            if len(extracted) == 1:
                continue
            max_created = max(map(lambda e: e.created_time, extracted))
            delete_ids = list(filter(lambda e: e.created_time != max_created, extracted))
            [client.functions.schedules.delete(j.id) for j in delete_ids]


def functions_exist_and_ready_external_ids(client: CogniteClient) -> List[str]:
    functions = client.functions.list()
    ready_air_functions = [f.external_id for f in functions if f.owner == "AIR" and f.status == "Ready"]
    return ready_air_functions


def execute(client: CogniteClient):
    missing_schedule_assets = retrieve_schedule_asset_without_asset(client)
    [create_asset(client, asset) for asset in missing_schedule_assets]
    to_be_deployed = retrieve_undeployed_infra_schedule_assets(client)
    existing_air_functions = functions_exist_and_ready_external_ids(client)
    # check if function exists
    existing_deployed = [model for model in to_be_deployed if model.model + MODEL_POSTFIX in existing_air_functions]
    if len(existing_deployed):
        create_schedules(client, existing_deployed)
    updated, to_be_deleted = retrieve_updated_infra_schedules(client)
    existing_updated = [model for model in updated if model.model + MODEL_POSTFIX in existing_air_functions]
    if len(existing_updated):
        update_schedules(client, existing_updated, to_be_deleted)
    print(f"Created: {len(existing_deployed)}, Updated: {len(existing_updated)}")
    infra_assets_names = map(lambda a: a.name, retrieve_infra_model_assets(client))
    infra_function_names = [asset + ":latest" for asset in infra_assets_names]
    delete_double_schedules(client, infra_function_names)
