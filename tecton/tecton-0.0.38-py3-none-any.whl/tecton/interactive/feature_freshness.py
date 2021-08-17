from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import Union

from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import sdk_public_method
from tecton._internals.utils import can_be_stale
from tecton._internals.utils import format_freshness_table
from tecton_proto.metadataservice.metadata_service_pb2 import GetAllFeatureFreshnessRequest


@sdk_public_method
def get_feature_freshness(workspace_name, to_dict: bool = False) -> Union[Dict[str, Dict], Displayable, str]:
    """
    Fetch freshness status for features

    :param: workspace_name: workspace to fetch freshness statuses of features from.
    :param: to_dict: return data as a Python dictionary. Otherwise, data is printed as a table.

    :return: Table or dictionary of freshness statuses for all features
    """
    fresh_request = GetAllFeatureFreshnessRequest()
    fresh_request.workspace = workspace_name
    fresh_response = metadata_service.instance().GetAllFeatureFreshness(fresh_request)

    if to_dict:
        to_return = {}
        for ff_proto in fresh_response.freshness_statuses:
            to_return[ff_proto.feature_view_name] = {
                "materialization_enabled": ff_proto.materialization_enabled,
                "is_stale": ff_proto.is_stale if can_be_stale(ff_proto) else None,
                "freshness": timedelta(seconds=ff_proto.freshness.seconds) if can_be_stale(ff_proto) else None,
                "expected_freshness": timedelta(seconds=ff_proto.expected_freshness.seconds)
                if can_be_stale(ff_proto)
                else None,
                "created": datetime.fromtimestamp(ff_proto.created_at.seconds),
                "is_stream": ff_proto.is_stream,
            }
        return to_return

    if len(fresh_response.freshness_statuses) == 0:
        return "No Feature Views found in this workspace"
    return format_freshness_table(fresh_response.freshness_statuses)
