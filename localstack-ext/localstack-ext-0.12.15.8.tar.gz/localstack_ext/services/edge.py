import contextlib
RXPEm=int
RXPEc=round
RXPEO=str
RXPES=True
RXPEx=set
RXPEz=len
RXPEM=None
RXPEd=any
RXPEu=list
RXPEY=Exception
RXPEt=ValueError
RXPEH=bytes
import io
import logging
import os
import re
import subprocess
import sys
import time
import traceback
import types
from zipfile import ZipFile
from localstack import config as localstack_config
from localstack import constants
from localstack.constants import APPLICATION_OCTET_STREAM
from localstack.services import edge as localstack_edge
from localstack.services import infra
from localstack.services.edge import PROXY_LISTENER_EDGE
from localstack.services.edge import ProxyListenerEdge as proxy
from localstack.services.plugins import SERIALIZERS
from localstack.utils import bootstrap
from localstack.utils.aws.aws_responses import(requests_error_response,requests_error_response_json,requests_response)
from localstack.utils.common import(TMP_THREADS,ShellCommandThread,get_free_tcp_port,rm_rf,sleep_forever,to_str)
from localstack.utils.testutil import create_zip_file
from requests.models import Request
from localstack_ext.constants import API_PATH_PODS
from localstack_ext.services.iam.policy_enforcer import(CACHED_POLICIES,enforce_iam_policies_for_request)
from localstack_ext.services.xray.xray_listener import XRAY_API_PATHS
from localstack_ext.utils.persistence import load_persisted_object
from localstack_ext.utils.state_merge import get_backend_state,merge_object_state
LOG=logging.getLogger(__name__)
IOT_PATH_PREFIXES=["/tags","/things","/thing-groups","/wireless-devices","/indices","/rules","/dimensions","/policies","/certificates","/jobs","/target-policies","/authorizer","/billing-groups","/domainConfigurations","/role-aliases","/streams","/thing-types","/dynamic-thing-groups"]
ACCOUNTS_TO_SERVICE_PORTS={}
STATE={}
def current_timestamp():
 return RXPEm(RXPEc(time.time()*1000))
def start_multi_account_router(parts,asynchronous):
 api_names=bootstrap.canonicalize_api_names()
 cmd="%s %s start --host"%(sys.executable,os.path.join(constants.LOCALSTACK_ROOT_FOLDER,"localstack","utils","cli.py"))
 reserved_ports=[]
 for account_id in parts:
  ACCOUNTS_TO_SERVICE_PORTS[account_id]=port_mappings={}
  services=""
  for api in api_names:
   port=get_free_tcp_port(blacklist=reserved_ports)
   reserved_ports.append(port)
   port_mappings[api]=port
   services+="%s%s:%s"%("," if services else "",api,port)
  edge_port=get_free_tcp_port(blacklist=reserved_ports)
  reserved_ports.append(edge_port)
  port_mappings["edge"]=edge_port
  LOG.debug("Using random service ports for account ID %s: %s"%(account_id,services))
  env_vars={"SERVICES":services,"EDGE_PORT":RXPEO(edge_port),"TEST_AWS_ACCOUNT_ID":account_id,"DNS_ADDRESS":"0","PYTHONPATH":".:%s"%constants.LOCALSTACK_ROOT_FOLDER}
  thread=ShellCommandThread(cmd,outfile=subprocess.PIPE,env_vars=env_vars)
  TMP_THREADS.append(thread)
  thread.start()
 localstack_edge.start_edge(asynchronous=RXPES)
 if not asynchronous:
  sleep_forever()
def patch_start_edge():
 from localstack_ext.services.apigateway.apigateway_extended import(is_custom_domain_api_invocation)
 from localstack_ext.services.cognito import cognito_utils
 def do_start_infra(asynchronous,*args,**kwargs):
  parts=re.split(r"[\s,;]+",constants.TEST_AWS_ACCOUNT_ID.strip())
  parts=RXPEx(parts)
  if RXPEz(parts)>1:
   return start_multi_account_router(parts,asynchronous)
  return do_start_infra_orig(asynchronous,*args,**kwargs)
 do_start_infra_orig=infra.do_start_infra
 infra.do_start_infra=do_start_infra
 def get_service_port_for_account(service,headers,*args,**kwargs):
  auth_header=headers.get("authorization","")
  credential=auth_header.split("Credential=")[-1]
  access_key=credential.split("/")[0]
  if ACCOUNTS_TO_SERVICE_PORTS:
   account_config=ACCOUNTS_TO_SERVICE_PORTS.get(access_key)or{}
   target_port=account_config.get("edge")
   if target_port:
    return target_port
   return-1
  return get_service_port_for_account_orig(service,headers,*args,**kwargs)
 get_service_port_for_account_orig=localstack_edge.get_service_port_for_account
 localstack_edge.get_service_port_for_account=get_service_port_for_account
 def get_api_from_headers(headers,method=RXPEM,path=RXPEM,data=RXPEM,**kwargs):
  auth_header=headers.get("authorization","")
  host=headers.get("host","")
  target=headers.get("x-amz-target","")
  path=path or "/"
  path_without_params=path.split("?")[0]
  if "/elasticmapreduce/" in auth_header:
   return "emr",localstack_config.PORT_EMR,path,host
  if cognito_utils.is_cognito_idp_request(path,headers):
   return "cognito-idp",localstack_config.PORT_COGNITO_IDP,path,host
  if path.startswith("/_messages_"):
   return "ses",localstack_config.PORT_SES,path,host
  if path=="/xray_records":
   return "xray",localstack_config.PORT_XRAY,path,host
  if target.startswith("AmazonAthena."):
   return "athena",localstack_config.PORT_ATHENA,path,host
  if target.startswith("AWSCognitoIdentityService."):
   return "cognito-identity",localstack_config.PORT_COGNITO_IDENTITY,path,host
  if ".cloudfront." in host:
   return "cloudfront",localstack_config.PORT_CLOUDFRONT,path,host
  if ".elb." in host:
   return "elbv2",localstack_config.PORT_ELBV2,path,host
  if "/execute-api/" in auth_header:
   if(RXPEd(path.startswith(prefix)for prefix in IOT_PATH_PREFIXES)or path_without_params=="/endpoint"):
    return "iot",localstack_config.PORT_IOT,path,host
   if path_without_params.startswith("/@connections/"):
    return "apigateway",localstack_config.PORT_APIGATEWAY,path,host
  if re.match(r"/graphql/[a-zA-Z0-9-]+",path):
   return "appsync",localstack_config.PORT_APPSYNC,path,host
  if ".appsync-api." in host:
   return "appsync",localstack_config.PORT_APPSYNC,path,host
  if "/elasticloadbalancing/" in auth_header:
   data_str=to_str(data or "")
   if RXPEd("Version=2015-12-01" in s for s in[path,data_str]):
    return "elbv2",localstack_config.PORT_ELBV2,path,host
   if RXPEd("Version=2012-06-01" in s for s in[path,data_str]):
    return "elb",localstack_config.PORT_ELB,path,host
  if "/2018-06-01/runtime" in path:
   return "lambda",localstack_config.PORT_LAMBDA,path,host
  if method=="POST" and path in XRAY_API_PATHS:
   return "xray",localstack_config.PORT_XRAY,path,host
  if auth_header.startswith("Bearer "):
   return "apigateway",localstack_config.PORT_APIGATEWAY,path,host
  result=get_api_from_headers_orig(headers,path=path,data=RXPEM,**kwargs)
  if result:
   result=RXPEu(result)
   if result[0]=="iotdata":
    result[0]="iot-data"
   if result[0]=="iotanalytics":
    result[0]="iot-analytics"
   if result[0]=="iotwireless":
    result[0]="iot"
   if result[0]=="elasticfilesystem":
    result[0]="efs"
   if result[0]!=localstack_edge.API_UNKNOWN:
    return result
  if not result or result[0]==localstack_edge.API_UNKNOWN:
   if is_custom_domain_api_invocation(method=method,path=path,data=data,headers=headers):
    return "apigateway",localstack_config.PORT_APIGATEWAY,path,host
  return result
 get_api_from_headers_orig=localstack_edge.get_api_from_headers
 localstack_edge.get_api_from_headers=get_api_from_headers
 def get_lock_for_request(api,method,path,data,headers,*args,**kwargs):
  serializer=SERIALIZERS.get(api)
  lock=RXPEM
  if serializer:
   request=Request(method=method,url=path,data=data,headers=headers)
   lock=serializer.get_lock_for_request(request)
  lock=lock or contextlib.nullcontext()
  return lock
 def return_response(self,method,path,data,headers,*args,**kwargs):
  api=get_api_from_headers(headers,method=method,path=path,data=data)[0]
  serializer=SERIALIZERS.get(api)
  lock=contextlib.nullcontext()
  if serializer:
   request=Request(method=method,url=path,data=data,headers=headers)
   context=serializer.get_context()
   serializer.update_state(context,request)
   lock=get_lock_for_request(api,method,path,data,headers,*args,**kwargs)
  with lock:
   return return_response_orig(self,method,path,data,headers,*args,**kwargs)
 return_response_orig=proxy.return_response
 proxy.return_response=return_response
 def do_forward_request(api,method,path,data,headers,*args,**kwargs):
  try:
   if api=="iam":
    CACHED_POLICIES.clear()
   enforce_iam_policies_for_request(api,method,path,data,headers)
  except RXPEY as e:
   kwargs={"message":"Access to the specified resource is denied","code":403,"error_type":"AccessDeniedException"}
   if api in["lambda"]:
    response=requests_error_response_json(**kwargs)
   else:
    response=requests_error_response(headers,**kwargs)
   t="" if "denied" in RXPEO(e)or "found" in RXPEO(e)else traceback.format_exc()
   LOG.debug('Denying request for API "%s" due to IAM enforcement: %s %s - %s %s'%(api,method,path,e,t))
   return response
  return do_forward_request_orig(api,method,path,data,headers,*args,**kwargs)
 do_forward_request_orig=localstack_edge.do_forward_request
 localstack_edge.do_forward_request=do_forward_request
 def forward_request(self,method,path,data,headers,*args,**kwargs):
  if path.startswith(API_PATH_PODS):
   return handle_pods_command(method,path,data,headers)
  return forward_request_orig(method,path,data,headers,*args,**kwargs)
 forward_request_orig=localstack_edge.PROXY_LISTENER_EDGE.forward_request
 localstack_edge.PROXY_LISTENER_EDGE.forward_request=types.MethodType(forward_request,PROXY_LISTENER_EDGE)
 import concurrent.futures
 from localstack.utils.async_utils import THREAD_POOL
 def _submit(self,*args,**kwargs):
  result=_submit_orig(self,*args,**kwargs)
  if not STATE.get("_queue_removed_"):
   STATE["_queue_removed_"]=RXPES
   try:
    del concurrent.futures.thread._threads_queues[RXPEu(THREAD_POOL._threads)[0]]
   except RXPEY:
    pass
  return result
 _submit_orig=THREAD_POOL.submit
 THREAD_POOL.submit=_submit
 patch_case_sensitive_headers()
def handle_pods_command(method,path,data,headers):
 LOG.debug("Handling pods request: %s %s"%(method,path))
 if method=="GET" and path==f"{API_PATH_PODS}/state":
  return handle_get_state_request(path,data)
 if method=="POST" and path==API_PATH_PODS:
  return handle_pod_state_injection(data)
 LOG.info("Unable to find handler for request: %s %s"%(method,path))
 return 404
def handle_get_state_request(path,data):
 if not localstack_config.DATA_DIR:
  return requests_response({"error":"Please configure DATA_DIR to manage local cloud pod state"},status_code=404)
 zip_contents=create_zip_file(localstack_config.DATA_DIR,get_content=RXPES)
 result=requests_response(zip_contents,headers={"Content-Type":APPLICATION_OCTET_STREAM})
 return result
def handle_pod_state_injection(pod_data):
 try:
  with ZipFile(io.BytesIO(pod_data),"r")as data_zip:
   data_zip.extractall("tmpdatadir")
 except RXPEY as e:
  LOG.warning(f"Failed to extract zip data from payload: {e}")
  return 400
 try:
  tmp_dir="./tmpdatadir/api_states"
  service_names=RXPEx()
  for dir_name,_,file_list in os.walk(tmp_dir):
   for fname in file_list:
    try:
     subdirs=os.path.normpath(dir_name).split(os.sep)
     region=subdirs[-1]
     service_name=subdirs[-2]
     service_names.add(service_name)
     memory_manager="moto" if fname=="backend_state" else "localstack"
     current_state=get_backend_state(service_name,region,memory_manager)
     deserialized_state=load_persisted_object(f"{dir_name}/{fname}")
     merge_object_state(current_state,deserialized_state)
    except RXPEY as e:
     LOG.warning(f"Failed to merge data for {fname} in dir {dir_name}: {e}")
     continue
  LOG.debug("Restored pod state from the following services: %s"%service_names)
  for service_name in service_names:
   serializer=SERIALIZERS.get(service_name)
   if serializer:
    serializer.update_state(serializer.get_context(),Request(method="POST",url="/",data="{}"))
  rm_rf(tmp_dir)
 except RXPEY as e:
  LOG.warning(f"Unable extract and restore pod state data: {e} {traceback.format_exc()}")
 return{}
def patch_case_sensitive_headers():
 from hypercorn import utils
 from hypercorn.protocol import http_stream
 from quart import asgi
 from quart import utils as quart_utils
 def _encode_headers(headers):
  return[(key.encode(),value.encode())for key,value in headers.items()]
 asgi._encode_headers=asgi.encode_headers=quart_utils.encode_headers=_encode_headers
 def build_and_validate_headers(headers):
  validated_headers=[]
  for name,value in headers:
   if name[0]==b":"[0]:
    raise RXPEt("Pseudo headers are not valid")
   validated_headers.append((RXPEH(name).strip(),RXPEH(value).strip()))
  return validated_headers
 utils.build_and_validate_headers=(http_stream.build_and_validate_headers)=build_and_validate_headers
# Created by pyminifier (https://github.com/liftoff/pyminifier)
