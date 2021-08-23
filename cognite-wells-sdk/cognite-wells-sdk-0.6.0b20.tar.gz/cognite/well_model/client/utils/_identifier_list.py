from typing import List, Optional

from cognite.well_model.models import Identifier


def identifier_list(
    asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
) -> Optional[List[Identifier]]:
    if asset_external_ids is None and matching_ids is None:
        return None

    identifiers = []
    for asset_external_id in asset_external_ids or []:
        identifiers.append(Identifier(asset_external_id=asset_external_id))
    for matching_id in matching_ids or []:
        identifiers.append(Identifier(matching_id=matching_id))
    return identifiers
