# Copyright 2020, castLabs GmbH

from .core.error import *
from .core.util import detect_bin, DEFAULT_HASH_BLOCK, hash_macho_wv0, hash_pe_wv0
from .core.failure import gather
from .auth import Auth

import builtins
from io import BytesIO
from sys import maxsize
from os import environ, path, rename, remove, makedirs
import errno
from datetime import datetime, timedelta
from binascii import a2b_base64, b2a_base64
import json
from glob import glob
from zlib import compress

from macholib import MachO, mach_o

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.x509 import load_der_x509_certificate, ObjectIdentifier
from cryptography.x509.oid import NameOID, ExtensionOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
from cryptography.exceptions import InvalidSignature

import requests

################################################################################

DEFAULT_API_URL = 'https://evs-api.castlabs.com'

################################################################################

ExtensionOID.VMP_DEVELOPMENT = ObjectIdentifier('1.3.6.1.4.1.11129.4.1.2')
ExtensionOID.VMP_PERSISTENT = ObjectIdentifier('1.3.6.1.4.1.11129.4.1.3')

STREAMING_SIGNATURE='streaming'
PERSISTENT_SIGNATURE='persistent'

SUBJECT_KEY_IDENTIFIERS = {
  STREAMING_SIGNATURE: [
    b'\x0f\x02\xae\xdf\xf7\xe5\xca\x19\nK\xc4$\xdb\xfat\xb5i\x97\x18\x8c',
    b'\xf8\xa3\xcbQZ\xe1\xc4\xe45\x07"n\x9eS\x13U\xe6\x85Y*'
  ],
  PERSISTENT_SIGNATURE: [
    b'\nmV\xb5\xae\x8e\xaf\x17\x16Y\x0e#\xd2lUS\xea\x7fW\xb5',
    b'\x0e\xb8ib\xf8\x9f\xaa\xc4h\xcbuP{Ih\x95B\x84\xbd]'
  ]
}
AUTHORITY_KEY_IDENTIFIERS = [ b'\xca=\xd8\x8e\x0ftW\x7f\xd0\x9a\xd9\xe1!\xbfB\xfb#U)\x86' ]

################################################################################

FLAGS_INTERMEDIATE = 0
FLAGS_FINAL = 1

################################################################################

class Signature(object):
  def __init__(self, fh):
    def decode_byte(fh):
      b = fh.read(1)
      return ord(b) if b else None
    def decode_leb128(f):
      shift = 0
      val = 0
      while True:
        b = decode_byte(f)
        if b is None:
          return None
        val |= (b & 0x7f) << shift
        if not (b & 0x80):
          break
        shift += 7
      return val
    def decode_bytes(fh):
      n = decode_leb128(fh)
      b = fh.read(n) if n is not None else None
      return b if b else None
    def decode_entry(f):
      return decode_byte(fh), decode_bytes(fh)
    self.version = decode_byte(fh)
    if self.version not in range(0, 1):
      raise UnsupportedError('Unsupported signature file version')
    self.cert, self.data, self.flags = None, None, None
    while True:
      tag, entry = decode_entry(fh)
      if tag is None:
        break
      if 1 == tag:
        self.cert = entry
      elif 2 == tag:
        self.data = entry
      elif 3 == tag:
        self.flags = entry
    if None in (self.cert, self.data, self.flags):
      raise InvalidDataError('Invalid signature file')
    if ord(self.flags) not in range(0, 2):
      raise InvalidDataError('Invalid signature file flags')

################################################################################

def hash_bin(bin):
  with open(bin, 'rb') as fh:
    fmt, p, a = detect_bin(fh)
    if fmt == 'macho':
      return hash_macho_wv0(fh), p, a
    elif fmt == 'pe':
      return hash_pe_wv0(fh), p, a
    raise UnsupportedError('Binary type or archtecture not supported')

def load_sig(bin, sig, p):
  if 'win32' == p:
    dir, name = path.split(bin)
    if name != 'electron.exe':
      o = path.join(dir, 'electron.exe.sig')
      if path.isfile(o):
        if not path.isfile(sig):
          rename(o, sig)
        elif not path.samefile(o, sig):
          remove(o)

  try:
    with open(sig, 'rb') as fh:
      return fh.read()
  except Exception as e:
    raise InvalidDataError('Failed to read signature') from e

def verify_dgt(dgt, sdata, kind, intermediate, min_days, any_ski=False, block_size=DEFAULT_HASH_BLOCK):
  try:
    s = Signature(BytesIO(sdata))
  except Exception as e:
    raise InvalidDataError('Failed to decode signature') from e

  expected_flags = FLAGS_INTERMEDIATE if intermediate else FLAGS_FINAL
  if ord(s.flags) != expected_flags:
    raise ValidityError('Signature flags do not match expected value')

  try:
    cert = load_der_x509_certificate(s.cert, backend=default_backend())
  except Exception as e:
    raise InvalidDataError('Failed to load certificate') from e
  try:
    cert.public_key().verify(s.data, dgt + s.flags, PSS(mgf=MGF1(SHA1()), salt_length=20), SHA1())
  except Exception as e:
    raise InvalidDataError('Failed to verify signature') from e

  now = datetime.now()
  if now < cert.not_valid_before:
    raise ValidityError('Certificate not yet valid')
  if min_days is not None and now > (cert.not_valid_after - timedelta(days=min_days)):
    raise ValidityError('Certificate expires in less than {} days'.format(min_days))
  days_left = (cert.not_valid_after - now).days

  ski = aki = ku = eku = vp = vd = None
  for e in cert.extensions:
    if ExtensionOID.SUBJECT_KEY_IDENTIFIER == e.oid:
      ski = e.value
    elif ExtensionOID.AUTHORITY_KEY_IDENTIFIER == e.oid:
      aki = e.value
    elif ExtensionOID.KEY_USAGE == e.oid:
      ku = e.value
    elif ExtensionOID.EXTENDED_KEY_USAGE == e.oid:
      eku = e.value
    elif ExtensionOID.VMP_PERSISTENT == e.oid:
      vp = e.value
    elif ExtensionOID.VMP_DEVELOPMENT == e.oid:
      vd = e.value
  if vd:
    raise ValidityError('Certificate is valid for development only')
  if (vp and STREAMING_SIGNATURE == kind) or (not vp and PERSISTENT_SIGNATURE == kind):
    raise ValidityError('Certificate doesn\'t match \'{}\' signature kind'.format(kind))
  if not eku or ExtendedKeyUsageOID.CODE_SIGNING not in eku:
    raise ValidityError('Certificate doesn\'t allow code signing')
  if not ku or not ku.digital_signature:
    raise ValidityError('Certificate doesn\'t allow digital signatures')
  if not aki or aki.key_identifier not in AUTHORITY_KEY_IDENTIFIERS:
    raise ValidityError('Certificate has invalid AuthorityKeyIdentifier')
  if not any_ski:
    if not ski or ski.digest not in SUBJECT_KEY_IDENTIFIERS.get(kind, []):
      raise ValidityError('Certificate has invalid SubjectKeyIdentifier')
  return '{}{}, {} days of validity'.format(kind, ', intermediate' if intermediate else '', days_left)

################################################################################

DEFAULT_CACHE_FILE = '~/.config/evs/cache.json'
DEFAULT_CACHE_MAX = 16

def _cache_key(dgt, p, a, kind, intermediate):
  return '{}-{}:{}{}:{}'.format(p, a, kind,
    '-intermediate' if intermediate else '',
    b2a_base64(dgt, newline=False).decode('utf-8')
  )

################################################################################

class VMP(Auth):
  def __init__(self, no_ask=True, any_ski=False, api_url=None, cache_file=None, cache_max=None, **_):
    self._any_ski = any_ski or 'EVS_ANY_SKI' in environ
    self._cache_file = path.expanduser(cache_file or environ.get('EVS_CACHE_FILE', DEFAULT_CACHE_FILE))
    self._cache_dir = path.dirname(self._cache_file)
    self._cache_max = int(cache_max or environ.get('EVS_CACHE_MAX', DEFAULT_CACHE_MAX))
    api_url = api_url or environ.get('EVS_API_URL', DEFAULT_API_URL)
    self.broker_url = '{}/{}'.format(api_url, 'broker')
    self.signer_url = '{}/{}'.format(api_url, 'signer')
    super().__init__(no_ask=no_ask)
    self._agent = '{}-{}'.format(__name__, self._version)
    self._load_cache()

  def _load_cache(self):
    try:
      with open(self._cache_file) as fh:
        self.__cache = json.load(fh)
    except:
      self.__cache = {}

  def _store_cache(self):
    if not self._cache_file:
      return False
    try:
      try:
        makedirs(self._cache_dir)
      except OSError as e:
        if errno.EEXIST != e.errno or not path.isdir(self._cache_dir):
          return False
      with open(self._cache_file, 'w') as fh:
        json.dump(self.__cache, fh, indent=2)
      return True
    except Exception as e:
      return False

  def _pop_cache_item(self, key):
    sdata = self.__cache.pop(key, None)
    if not sdata:
      return None
    return a2b_base64(sdata)

  def _add_cache_item(self, key, sdata):
    if key in self.__cache:
      del self.__cache[key]
    self.__cache[key] = b2a_base64(sdata, newline=False).decode('utf-8')
    while len(self.__cache) > self._cache_max:
      del self.__cache[next(iter(self.__cache))]

  def _request_upload(self, gz=False):
    try:
      ps = {
        'agent': self._agent,
        **({'gz': ''} if gz else {})
      }
      while True:
        r = requests.get(self.broker_url,
          params=ps,
          headers={
            'Authorization': self._auth_id_token,
            'Accept': 'application/json',
          }
        )
        if r.status_code not in (401, 403) or not self._refresh_auth():
          break
    except Exception as e:
      raise RequestError('Request for upload URL failed') from e
    try:
      j = r.json()
    except Exception as e:
      raise InvalidDataError('Failed to parse JSON body in upload URL response') from e
    if r.status_code != 200 or 'errorMessage' in j or 'message' in j:
      e = gather(j)
      raise HTTPError('Request for upload URL failed: {} {}'.format(r.status_code, r.reason)) from e
    if 'key' not in j:
      raise InvalidDataError('No \'key\' returned in upload URL response')
    if 'url' not in j:
      raise InvalidDataError('No \'url\' returned in upload URL response')
    return (j['key'], j['url'])

  def _upload_data(self, data, gz=False):
    key, url = self._request_upload(gz)
    gz = key.endswith('.gz')
    try:
      r = requests.put(url,
        data=data if not gz else compress(data.read()),
        headers={
          'Content-Type': 'application/octet-stream' if not gz else 'application/gzip',
        }
      )
    except Exception as e:
      raise RequestError('Upload request failed') from e
    if r.status_code != 200:
      raise HTTPError('Upload request failed: {} {}'.format(r.status_code, r.reason))
    return key

  def _upload_file(self, bin, gz=False):
    with open(bin, 'rb') as fh:
      return self._upload_data(fh, gz)

  def _sign(self, key, kind, intermediate=False):
    try:
      ps = {
        'agent': self._agent,
        'key': key,
        'kind': kind,
        **({'intermediate': ''} if intermediate else {})
      }
      while True:
        r = requests.get(self.signer_url,
          params=ps,
          headers={
            'Authorization': self._auth_id_token,
            'Accept': 'application/json',
          }
        )
        if r.status_code not in (401, 403) or not self._refresh_auth():
          break
    except Exception as e:
      raise RequestError('Signing request failed') from e
    try:
      j = r.json()
    except Exception as e:
      raise InvalidDataError('Failed to parse JSON body in signing response') from e
    if r.status_code != 200 or 'errorMessage' in j or 'message' in j:
      e = gather(j)
      raise HTTPError('Signing request failed: {} {}'.format(r.status_code, r.reason)) from e
    if 'key' not in j:
      raise InvalidDataError('No \'key\' returned in signing response')
    if key != j['key']:
      raise InvalidDataError('Mismatching \'key\' returned in signing response')
    if 'sig' not in j:
      raise InvalidDataError('No \'sig\' returned in signing response')
    return a2b_base64(j['sig'])

  def _store(self, sig, sdata):
    with open(sig, 'wb') as fh:
      fh.write(sdata)

  def verify(self, bin, sig=None, kind=None, intermediate=False, min_days=None, app=None, **_):
    sig = sig or (bin + '.sig')
    kind = kind or environ.get('EVS_KIND', STREAMING_SIGNATURE)
    intermediate = intermediate or 'EVS_INTERMEDIATE' in environ
    print('Verifying signature for: {}'.format(app or bin))
    dgt, p, _ = hash_bin(bin)
    msg = verify_dgt(dgt, load_sig(bin, sig, p), kind, intermediate, min_days, self._any_ski)
    print(' - Signature is valid [{}]'.format(msg))

  def sign(self, bin, sig=None, kind=None, intermediate=False, min_days=None, force=False, gz=False, account_name=None, passwd=None, app=None, **_):
    sig = sig or (bin + '.sig')
    key = environ.get('EVS_KEY', None)
    kind = kind or environ.get('EVS_KIND', STREAMING_SIGNATURE)
    intermediate = intermediate or 'EVS_INTERMEDIATE' in environ
    force = force or 'EVS_FORCE' in environ
    print('Signing: {}'.format(app or bin))
    dgt, p, a = hash_bin(bin)
    ckey = _cache_key(dgt, p, a, kind, intermediate)
    sdata = None
    if not force:
      print(' - Verifying existing VMP signature')
      try:
        sdata = load_sig(bin, sig, p)
        msg = verify_dgt(dgt, sdata, kind, intermediate, min_days, self._any_ski)
        print(' - Signature is valid [{}], forego signing'.format(msg))
        return
      except Exception as e:
        print(' - Signature invalid:', e)
      sdata = self._pop_cache_item(ckey)
      if sdata:
        print(' - Verifying matching VMP signature in cache')
        try:
          msg = verify_dgt(dgt, sdata, kind, intermediate, min_days, self._any_ski)
          print(' - Signature is valid [{}], use cached signature'.format(msg))
        except Exception as e:
          print(' - Signature invalid:', e)
          sdata = None
    if not sdata:
      print(' - Requesting VMP signature')
      self._check_auth(account_name, passwd)
      sdata = self._sign(key or self._upload_file(bin, gz), kind, intermediate)
    self._add_cache_item(ckey, sdata)
    self._store_cache()
    self._store(sig, sdata)

  def _detect_pkgs(self, dirs, name_hint=None):
    def _to_pattern(n):
      return ''.join(('[{}{}]'.format(c.upper(), c.lower()) if c.isalpha() else c) for c in n)
    def _try_app(app):
      if path.isdir(app):
        fwdir = 'Contents/Frameworks/Electron Framework.framework/Versions/A'
        fwbin = path.join(app, fwdir, 'Electron Framework')
        if path.isfile(fwbin):
          fwsig = path.join(app, fwdir, 'Resources/Electron Framework.sig')
          return (app, fwbin, fwsig)
      return None
    def _try_exe(exe):
      if path.isfile(exe):
        sig = '{}.sig'.format(exe)
        return (exe, exe, sig)
      return None
    def _try_dir(dir, patterns):
      for p in patterns:
        p = path.join(dir, p)
        for m in glob('{}.app'.format(p)):
          item = _try_app(m)
          if item: return item
        for m in glob('{}.exe'.format(p)):
          item = _try_exe(m)
          if item: return item
      raise FileNotFoundError('No matching executable found in: {}'.format(dir))

    patterns = []
    if not name_hint:
      patterns.append(_to_pattern('electron'))
      patterns.append('*')
    else:
      patterns.append(_to_pattern(name_hint))
    return [ _try_dir(dir, patterns) for dir in dirs ]

  def verify_pkg(self, pkg, name_hint=None, kind=None, min_days=None, **_):
    items = self._detect_pkgs(pkg if isinstance(pkg, list) else [ pkg ], name_hint)
    for item in items:
      self.verify(item[1], item[2], kind, False, min_days, app=item[0])

  def sign_pkg(self, pkg, name_hint=None, kind=None, min_days=None, force=False, gz=False, account_name=None, passwd=None, **_):
    items = self._detect_pkgs(pkg if isinstance(pkg, list) else [ pkg ], name_hint)
    for item in items:
      self.sign(item[1], item[2], kind, False, min_days, force, gz, account_name, passwd, app=item[0])

################################################################################

if __name__ == '__main__':
  from .cli.vmp import main
  main()

################################################################################
