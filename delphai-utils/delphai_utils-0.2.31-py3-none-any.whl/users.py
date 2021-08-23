from typing import Dict, List, Tuple, Union
from base64 import b64decode
import json
from grpc.aio import ServicerContext


def get_user(context: ServicerContext) -> Dict:
  """
  Get x-delphai-user information.

  :param grpc.aio.ServicerContext context: context passed to grpc endpoints
  :raises: KeyError
  :return x-delphai-user dictionary.
    More information: https://wiki.delphai.dev/wiki/Authorization
  :rtype: Dict
  """

  metadata = dict(context.invocation_metadata())
  user64 = metadata['x-delphai-user']
  user = b64decode(user64)
  return json.loads(user)


def get_groups(context: ServicerContext) -> List[str]:
  """
  Gets groups of calling identity

  :param grpc.aio.ServicerContext context: context passed to grpc endpoints
  :return raw roles passed from keycloak.
    For example this can be ["/delphai/Development"]
  :rtype List[str]
  """

  assert isinstance(context, object)
  try:
    user = get_user(context)
  except KeyError:
    return []
  return user.get('groups') or []


def get_affiliation(context: ServicerContext) -> Tuple[Union[str, None], Union[str, None]]:
  """
  Gets organization and department of user

  :param grpc.aio.ServicerContext context: context passed to grpc endpoints
  :return organization and department as a tuple or None if not affiliated
  :rtype Union[Tuple[str, None], Tuple[str, None]]
  """

  raw_groups = get_groups(context)
  if len(raw_groups) == 0:
    return None, None
  else:
    group_hirarchy = raw_groups[0].split('/')[1:3]
    if len(group_hirarchy) == 1:
      return group_hirarchy.pop(), None
    elif len(group_hirarchy) == 2:
      return tuple(group_hirarchy)
    else:
      return None, None


def get_user_and_client_ids(context: ServicerContext) -> Tuple[str, str]:
  """
  Get user_id and client_id.

  :param grpc.aio.ServicerContext context: context passed to grpc endpoints
  :return user_id and client_id.
    More information: https://wiki.delphai.dev/wiki/Authorization
  :rtype: Tuple[str, str]
  """
  try:
    user = get_user(context)
    user_id = user.get('https://delphai.com/mongo_user_id')
    client_id = user.get('https://delphai.com/client_id')
  except Exception:
    return '', ''
  return user_id, client_id
