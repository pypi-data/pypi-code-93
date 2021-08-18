from tim.core.credentials import Credentials
from tim.core.api import execute_request
from .types import WorkspaceListPayload, Workspace
from typing import List, Union


def get_workspaces(
    credentials: Credentials,
    offset: int,
    limit: int,
    userGroupId: Union[str, None] = None,
    sort: Union[str, None] = None
) -> List[Workspace]:
  payload = WorkspaceListPayload(offset=offset, limit=limit)
  if userGroupId: payload['userGroupId'] = userGroupId
  if sort: payload['sort'] = sort

  return execute_request(
      credentials=credentials, method='get', path=f'/workspaces', params=payload
  )
