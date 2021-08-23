import base64
ivkIj=True
ivkIH=Exception
ivkIq=False
ivkIP=str
ivkIN=len
ivkIX=int
ivkIs=range
ivkIh=object
import glob
import json
import logging
import os
import re
import sys
import traceback
import pyaes
from localstack import config as localstack_config
from localstack.constants import ENV_PRO_ACTIVATED
from localstack.utils.common import load_file,md5,now_utc,parallelize
from localstack.utils.common import safe_requests as requests
from localstack.utils.common import save_file,str_insert,str_remove,to_bytes,to_str
from localstack_ext import __version__,config
from localstack_ext.config import PROTECTED_FOLDERS,ROOT_FOLDER
ENV_PREPARED={}
MAX_KEY_CACHE_DURATION_SECS=60*60*24
LOG=logging.getLogger(__name__)
ENV_LOCALSTACK_API_KEY="LOCALSTACK_API_KEY"
def read_api_key(raise_if_missing=ivkIj):
 key=(os.environ.get(ENV_LOCALSTACK_API_KEY)or "").strip()
 if not key and raise_if_missing:
  raise ivkIH("Unable to retrieve API key. Please configure $%s in your environment"%ENV_LOCALSTACK_API_KEY)
 return key
def fetch_key():
 api_key=read_api_key()
 if api_key=="test":
  return "test"
 data={"api_key":api_key,"version":__version__}
 try:
  logging.getLogger("py.warnings").setLevel(logging.ERROR)
  result=requests.post("%s/activate"%config.API_URL,json.dumps(data),verify=ivkIq)
  if result.status_code>=400:
   content=result.content
   content_type=result.headers.get("Content-Type")
   raise ivkIH('Received error activating key (code %s): ctype "%s" - %s'%(result.status_code,content_type,content))
  key_base64=json.loads(to_str(result.content))["key"]
  cache_key_locally(api_key,key_base64)
 except ivkIH as e:
  if log_license_issues():
   api_key=ivkIP(api_key_configured()or "")
   api_key_prefix=api_key[:3]
   LOG.warning('Error activating API key "%s..."(%s): %s %s'%(api_key_prefix,ivkIN(api_key),e,traceback.format_exc()))
  key_base64=load_cached_key(api_key)
 finally:
  logging.getLogger("py.warnings").setLevel(logging.WARNING)
 decoded_key=to_str(base64.b64decode(key_base64))
 return decoded_key
def cache_key_locally(api_key,key_b64):
 configs=localstack_config.load_config_file()
 timestamp=ivkIP(ivkIX(now_utc()))
 key_raw=to_str(base64.b64decode(key_b64))
 for i in ivkIs(ivkIN(timestamp)):
  key_raw=str_insert(key_raw,i*2,timestamp[i])
 key_b64=to_str(base64.b64encode(to_bytes(key_raw)))
 configs["cached_key"]={"timestamp":ivkIX(timestamp),"key_hash":md5(api_key),"key":key_b64}
 save_file(localstack_config.CONFIG_FILE_PATH,json.dumps(configs))
 return configs
def load_cached_key(api_key):
 configs=localstack_config.load_config_file()
 cached_key=configs["cached_key"]
 if cached_key.get("key_hash")!=md5(api_key):
  raise ivkIH("Cached key was created for a different API key")
 now=now_utc()
 if(now-cached_key["timestamp"])>MAX_KEY_CACHE_DURATION_SECS:
  raise ivkIH("Cached key expired")
 timestamp=ivkIP(cached_key["timestamp"])
 key_raw=to_str(base64.b64decode(cached_key["key"]))
 for i in ivkIs(ivkIN(timestamp)):
  assert key_raw[i]==timestamp[i]
  key_raw=str_remove(key_raw,i)
 key_b64=to_str(base64.b64encode(to_bytes(key_raw)))
 return key_b64
def generate_aes_cipher(key):
 key=to_bytes(key)
 return pyaes.AESModeOfOperationCBC(key,iv="\0"*16)
def decrypt_file(source,target,key):
 cipher=generate_aes_cipher(key)
 raw=load_file(source,mode="rb")
 decrypter=pyaes.Decrypter(cipher)
 decrypted=decrypter.feed(raw)
 decrypted+=decrypter.feed()
 decrypted=decrypted.partition(b"\0")[0]
 decrypted=to_str(decrypted)
 save_file(target,content=decrypted)
def decrypt_files(key):
 files=[]
 for folder in PROTECTED_FOLDERS:
  for subpath in("*.py.enc","**/*.py.enc"):
   for f in glob.glob("%s/localstack_ext/%s/%s"%(ROOT_FOLDER,folder,subpath)):
    files.append(f)
 def _decrypt(f):
  target=f[:-4]
  if not os.path.exists(target):
   decrypt_file(f,target,key)
 parallelize(_decrypt,files)
def cleanup_environment():
 excepted_files=r".*/services/((edge)|(dns_server)|(__init__))\.py"
 for folder in PROTECTED_FOLDERS:
  for subpath in("*.py.enc","**/*.py.enc"):
   for f in glob.glob("%s/localstack_ext/%s/%s"%(ROOT_FOLDER,folder,subpath)):
    target=f[:-4]
    if not re.match(excepted_files,target):
     for delete_file in(target,"%sc"%target):
      if os.path.exists(delete_file):
       os.remove(delete_file)
def prepare_environment():
 class OnClose(ivkIh):
  def __exit__(self,*args,**kwargs):
   if not ENV_PREPARED.get("finalized"):
    cleanup_environment()
   ENV_PREPARED["finalized"]=ivkIj
  def __enter__(self,*args,**kwargs):
   pass
 if not ENV_PREPARED.get("finalized"):
  try:
   key=fetch_key()
   if not key:
    raise ivkIH("Unable to fetch and validate API key from environment")
   if key!="test":
    decrypt_files(key)
    LOG.info("Successfully activated API key")
   else:
    LOG.info("Using test API key")
   os.environ[ENV_PRO_ACTIVATED]="1"
  except ivkIH as e:
   if log_license_issues():
    LOG.warning("Unable to activate API key: %s %s"%(e,traceback.format_exc()))
   if config.REQUIRE_PRO:
    LOG.error("Unable to activate API key, but $REQUIRE_PRO is configured - quitting.")
    sys.exit(1)
 return OnClose()
def log_license_issues():
 return api_key_configured()and localstack_config.is_env_true("LOG_LICENSE_ISSUES")
def api_key_configured():
 return read_api_key(raise_if_missing=ivkIq)
def get_auth_headers():
 configs=localstack_config.load_config_file()
 login_info=configs.get("login")
 if not login_info:
  raise ivkIH("Please log in first")
 auth_token=login_info["token"]
 if not auth_token.startswith("%s "%login_info["provider"]):
  auth_token="%s %s"%(login_info["provider"],auth_token)
 headers={"authorization":auth_token}
 return headers
# Created by pyminifier (https://github.com/liftoff/pyminifier)
