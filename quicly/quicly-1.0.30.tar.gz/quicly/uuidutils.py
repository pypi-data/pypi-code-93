from typing import *

from quicly.patterns import PATTERN_UUID

from bson import ObjectId
from uuid import UUID, uuid4


class QxUuidUtils(object):
  @staticmethod
  def mk_uuid(v: Any = None, sp: Optional[str] = '-') -> str:
    if isinstance(v, ObjectId):
      ret = str(v)
    elif isinstance(v, UUID):
      ret = str(v).replace('-', '')
    elif isinstance(v, str) and PATTERN_UUID.fullmatch(v):
      ret = ''.join(PATTERN_UUID.findall(v))
    else:
      ret = str(ObjectId())

    if isinstance(sp, str) and len(sp):
      ret = sp.join([ret[0:8], ret[8:12],  ret[12:16], ret[16:20], ret[20:32]])

    return ret
