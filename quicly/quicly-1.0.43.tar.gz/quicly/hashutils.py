from typing import *

import os
import hashlib


class QxHash(object):
  MD5 = 'md5'
  SHA1 = 'sha1'
  SHA224 = 'sha224'
  SHA256 = 'sha256'
  SHA384 = 'sha384'
  SHA512 = 'sha512'
  BLAKE2B = 'blake2b'
  BLAKE2S = 'blake2s'
  SHA3_224 = 'sha3_224'
  SHA3_256 = 'sha3_256'
  SHA3_384 = 'sha3_384'
  SHA3_512 = 'sha3_512'
  SHAKE_128 = 'shake_128'
  SHAKE_256 = 'shake_256'

  def __init__(self, algorithm: str = SHA1):
    self._hash_o = getattr(hashlib, algorithm)
    assert callable(self._hash_o)

  def hash_s(self, s: Union[str, bytes]) -> str:
    if isinstance(s, str):
      s = s.encode('utf-8')
    h = self._hash_o()
    h.update(s)
    return h.hexdigest().lower()

  def hash_f(self, f: str) -> str:
    ret = None
    if os.path.isfile(f):
      with open(f, 'rb') as fo:
        ret = self.hash_s(fo.read())
    elif os.path.isdir(f):
      lines = []
      for item in sorted(os.listdir(f)):
        pathname = os.path.join(f, item)
        lines.append('{}:{}'.format(item, self.hash_f(pathname)))
      ret = self.hash_s('\n'.join(lines))
    return ret
