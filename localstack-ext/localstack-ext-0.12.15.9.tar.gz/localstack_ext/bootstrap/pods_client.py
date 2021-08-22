import json
wkueb=None
wkueV=object
wkueI=Exception
wkueh=set
wkuer=property
wkuej=classmethod
wkueW=False
wkueA=True
wkuec=len
wkuep=getattr
wkueG=type
wkues=isinstance
wkuey=list
wkueD=str
import logging
import os
import re
from typing import List
import requests
import yaml
from dulwich import porcelain
from dulwich.client import get_transport_and_path_from_url
from dulwich.repo import Repo
from localstack import config
from localstack.constants import API_ENDPOINT
from localstack.utils.common import(chmod_r,clone,cp_r,disk_usage,download,format_number,is_command_available,load_file,mkdir,new_tmp_dir,new_tmp_file,retry,rm_rf,run,safe_requests,save_file,to_bytes,to_str,unzip)
from localstack.utils.testutil import create_zip_file
from localstack_ext.bootstrap.licensing import get_auth_headers
from localstack_ext.constants import API_PATH_PODS
LOG=logging.getLogger(__name__)
PERSISTED_FOLDERS=["api_states","dynamodb","kinesis"]
class PodInfo:
 def __init__(self,name=wkueb,pod_size=0):
  self.name=name
  self.pod_size=pod_size
  self.pod_size_compressed=0
  self.persisted_resource_names=[]
class CloudPodManager(wkueV):
 BACKEND="_none_"
 def __init__(self,pod_name=wkueb,config=wkueb):
  self.pod_name=pod_name
  self._pod_config=config
 def push(self)->PodInfo:
  raise wkueI("Not implemented")
 def pull(self):
  raise wkueI("Not implemented")
 def restart_container(self):
  LOG.info("Restarting LocalStack instance with updated persistence state - this may take some time ...")
  data={"action":"restart"}
  url="%s/health"%config.get_edge_url()
  try:
   requests.post(url,data=json.dumps(data))
  except requests.exceptions.ConnectionError:
   pass
  def check_status():
   LOG.info("Waiting for LocalStack instance to be fully initialized ...")
   response=requests.get(url)
   content=json.loads(to_str(response.content))
   statuses=[v for k,v in content["services"].items()]
   assert wkueh(statuses)==wkueh(["running"])
  retry(check_status,sleep=3,retries=10)
 @wkuer
 def pod_config(self):
  return self._pod_config or PodConfigManager.pod_config(self.pod_name)
 @wkuej
 def get(cls,pod_name,pre_config=wkueb):
  pod_config=pre_config if pre_config else PodConfigManager.pod_config(pod_name)
  backend=pod_config.get("backend")
  for clazz in cls.__subclasses__():
   if clazz.BACKEND==backend:
    return clazz(pod_name=pod_name,config=pod_config)
  raise wkueI('Unable to find Cloud Pod manager implementation type "%s"'%backend)
 def deploy_pod_into_instance(self,pod_path):
  delete_pod_zip=wkueW
  if os.path.isdir(pod_path):
   tmpdir=new_tmp_dir()
   for folder in PERSISTED_FOLDERS:
    src_folder=os.path.join(pod_path,folder)
    tgt_folder=os.path.join(tmpdir,folder)
    cp_r(src_folder,tgt_folder,rm_dest_on_conflict=wkueA)
   pod_path=create_zip_file(tmpdir)
   rm_rf(tmpdir)
   delete_pod_zip=wkueA
  zip_content=load_file(pod_path,mode="rb")
  url=self.get_pods_endpoint()
  result=requests.post(url,data=zip_content)
  if result.status_code>=400:
   raise wkueI("Unable to restore pod state via local pods management API %s (code %s): %s"%(url,result.status_code,result.content))
  if delete_pod_zip:
   rm_rf(pod_path)
  else:
   return pod_path
 def get_state_zip_from_instance(self,get_content=wkueW):
  url=f"{self.get_pods_endpoint()}/state"
  result=requests.get(url)
  if result.status_code>=400:
   raise wkueI("Unable to get local pod state via management API %s (code %s): %s"%(url,result.status_code,result.content))
  if get_content:
   return result.content
  zip_file=f"{new_tmp_file()}.zip"
  save_file(zip_file,result.content)
  return zip_file
 def get_pods_endpoint(self):
  edge_url=config.get_edge_url()
  return f"{edge_url}{API_PATH_PODS}"
 def get_pod_info(self,pod_data_dir:wkueD=wkueb):
  result=PodInfo(self.pod_name)
  if pod_data_dir:
   result.pod_size=disk_usage(pod_data_dir)
   result.persisted_resource_names=get_persisted_resource_names(pod_data_dir)
  return result
class CloudPodManagerFilesystem(CloudPodManager):
 BACKEND="file"
 def push(self)->PodInfo:
  local_folder=self.target_folder()
  print('Pushing state of cloud pod "%s" to local folder: %s'%(self.pod_name,local_folder))
  mkdir(local_folder)
  zip_file=self.get_state_zip_from_instance()
  unzip(zip_file,local_folder)
  chmod_r(local_folder,0o777)
  result=self.get_pod_info(local_folder)
  print("Done.")
  return result
 def pull(self):
  local_folder=self.target_folder()
  if not os.path.exists(local_folder):
   print('WARN: Local path of cloud pod "%s" does not exist: %s'%(self.pod_name,local_folder))
   return
  print('Pulling state of cloud pod "%s" from local folder: %s'%(self.pod_name,local_folder))
  self.deploy_pod_into_instance(local_folder)
 def target_folder(self):
  local_folder=re.sub(r"^file://","",self.pod_config.get("url",""))
  return local_folder
class CloudPodManagerManaged(CloudPodManager):
 BACKEND="managed"
 def push(self)->PodInfo:
  presigned_url=self.presigned_url("push")
  zip_data_content=self.get_state_zip_from_instance(get_content=wkueA)
  print('Pushing state of cloud pod "%s" to backend server (%s KB)'%(self.pod_name,format_number(wkuec(zip_data_content)/1000.0)))
  res=safe_requests.put(presigned_url,data=zip_data_content)
  if res.status_code>=400:
   raise wkueI("Unable to push pod state to API (code %s): %s"%(res.status_code,res.content))
  print("Done.")
  result=self.get_pod_info()
  result.pod_size_compressed=wkuec(zip_data_content)
  return result
 def pull(self):
  presigned_url=self.presigned_url("pull")
  print('Pulling state of cloud pod "%s" from managed storage'%self.pod_name)
  zip_path=new_tmp_file()
  download(presigned_url,zip_path)
  self.deploy_pod_into_instance(zip_path)
  rm_rf(zip_path)
 def presigned_url(self,mode):
  data={"pod_name":self.pod_name,"mode":mode}
  data=json.dumps(data)
  auth_headers=get_auth_headers()
  response=safe_requests.post("%s/cloudpods/data"%API_ENDPOINT,data,headers=auth_headers)
  content=response.content
  if response.status_code>=400:
   raise wkueI("Unable to push cloud pod to API (code %s): %s"%(response.status_code,content))
  content=json.loads(to_str(content))
  return content["presignedURL"]
class CloudPodManagerGit(CloudPodManager):
 BACKEND="git"
 def push(self):
  repo=self.local_repo()
  branch=to_bytes(self.pod_config.get("branch"))
  remote_location=self.pod_config.get("url")
  try:
   porcelain.pull(repo,remote_location,refspecs=branch)
  except wkueI as e:
   LOG.info("Unable to pull repo: %s"%e)
  zip_file=self.get_state_zip_from_instance()
  tmp_data_dir=new_tmp_dir()
  unzip(zip_file,tmp_data_dir)
  is_empty_repo=b"HEAD" not in repo or repo.refs.allkeys()==wkueh([b"HEAD"])
  if is_empty_repo:
   LOG.debug("Initializing empty repository %s"%self.clone_dir)
   init_file=os.path.join(self.clone_dir,".init")
   save_file(init_file,"")
   porcelain.add(repo,init_file)
   porcelain.commit(repo,message="Initial commit")
  if branch not in repo:
   porcelain.branch_create(repo,branch,force=wkueA)
  self.switch_branch(branch)
  for folder in PERSISTED_FOLDERS:
   LOG.info("Copying persistence folder %s to local git repo %s"%(folder,self.clone_dir))
   src_folder=os.path.join(tmp_data_dir,folder)
   tgt_folder=os.path.join(self.clone_dir,folder)
   cp_r(src_folder,tgt_folder)
   files=tgt_folder
   if os.path.isdir(files):
    files=[os.path.join(root,f)for root,_,files in os.walk(tgt_folder)for f in files]
   if files:
    porcelain.add(repo,files)
  porcelain.commit(repo,message="Update state")
  porcelain.push(repo,remote_location,branch)
 def pull(self):
  repo=self.local_repo()
  client,path=self.client()
  remote_refs=client.fetch(path,repo)
  branch=self.pod_config.get("branch")
  remote_ref=b"refs/heads/%s"%to_bytes(branch)
  if remote_ref not in remote_refs:
   raise wkueI('Unable to find branch "%s" in remote git repo'%branch)
  remote_location=self.pod_config.get("url")
  self.switch_branch(branch)
  branch_ref=b"refs/heads/%s"%to_bytes(branch)
  from dulwich.errors import HangupException
  try:
   porcelain.pull(repo,remote_location,branch_ref)
  except HangupException:
   pass
  self.deploy_pod_into_instance(self.clone_dir)
 def client(self):
  client,path=get_transport_and_path_from_url(self.pod_config.get("url"))
  return client,path
 def local_repo(self):
  self.clone_dir=wkuep(self,"clone_dir",wkueb)
  if not self.clone_dir:
   pod_dir_name=re.sub(r"(\s|/)+","",self.pod_name)
   self.clone_dir=os.path.join(config.TMP_FOLDER,"pods",pod_dir_name,"repo")
   mkdir(self.clone_dir)
   if not os.path.exists(os.path.join(self.clone_dir,".git")):
    porcelain.clone(self.pod_config.get("url"),self.clone_dir)
  return Repo(self.clone_dir)
 def switch_branch(self,branch):
  repo=self.local_repo()
  if is_command_available("git"):
   return run("cd %s; git checkout %s"%(self.clone_dir,to_str(branch)))
  branch_ref=b"refs/heads/%s"%to_bytes(branch)
  if branch_ref not in repo.refs:
   branch_ref=b"refs/remotes/origin/%s"%to_bytes(branch)
  repo.reset_index(repo[branch_ref].tree)
  repo.refs.set_symbolic_ref(b"HEAD",branch_ref)
class PodConfigManagerMeta(wkueG):
 def __getattr__(cls,attr):
  def _call(*args,**kwargs):
   result=wkueb
   for manager in cls.CHAIN:
    try:
     tmp=wkuep(manager,attr)(*args,**kwargs)
     if tmp:
      if not result:
       result=tmp
      elif wkues(tmp,wkuey)and wkues(result,wkuey):
       result.extend(tmp)
    except wkueI:
     pass
   if result is not wkueb:
    return result
   raise wkueI('Unable to run operation "%s" for local or remote configuration'%attr)
  return _call
class PodConfigManager(wkueV,metaclass=PodConfigManagerMeta):
 CHAIN=[]
 @wkuej
 def pod_config(cls,pod_name):
  pods=PodConfigManager.list_pods()
  pod_config=[pod for pod in pods if pod["pod_name"]==pod_name]
  if not pod_config:
   raise wkueI('Unable to find config for pod named "%s"'%pod_name)
  return pod_config[0]
class PodConfigManagerLocal(wkueV):
 CONFIG_FILE=".localstack.yml"
 def list_pods(self):
  local_pods=self._load_config(safe=wkueA).get("pods",{})
  local_pods=[{"pod_name":k,"state":"Local Only",**v}for k,v in local_pods.items()]
  existing_names=wkueh([pod["pod_name"]for pod in local_pods])
  result=[pod for pod in local_pods if pod["pod_name"]not in existing_names]
  return result
 def store_pod_metadata(self,pod_name,metadata):
  pass
 def _load_config(self,safe=wkueW):
  try:
   return yaml.load(to_str(load_file(self.CONFIG_FILE)))
  except wkueI:
   if safe:
    return{}
   raise wkueI('Unable to find and parse config file "%s"'%self.CONFIG_FILE)
class PodConfigManagerRemote(wkueV):
 def list_pods(self):
  result=[]
  auth_headers=get_auth_headers()
  response=safe_requests.get("%s/cloudpods"%API_ENDPOINT,headers=auth_headers)
  content=response.content
  if response.status_code>=400:
   raise wkueI("Unable to fetch list of pods from API (code %s): %s"%(response.status_code,content))
  remote_pods=json.loads(to_str(content)).get("cloudpods",[])
  remote_pods=[{"state":"Shared",**pod}for pod in remote_pods]
  result.extend(remote_pods)
  return result
 def store_pod_metadata(self,pod_name,metadata):
  auth_headers=get_auth_headers()
  metadata["pod_name"]=pod_name
  response=safe_requests.post("%s/cloudpods"%API_ENDPOINT,json.dumps(metadata),headers=auth_headers)
  content=response.content
  if response.status_code>=400:
   raise wkueI("Unable to store pod metadata in API (code %s): %s"%(response.status_code,content))
  return json.loads(to_str(content))
PodConfigManager.CHAIN.append(PodConfigManagerLocal())
PodConfigManager.CHAIN.append(PodConfigManagerRemote())
def push_state(pod_name,args,**kwargs):
 pre_config=kwargs.get("pre_config",wkueb)
 backend=CloudPodManager.get(pod_name=pod_name,pre_config=pre_config)
 pod_config=clone(backend.pod_config)
 pod_info=backend.push()
 pod_config["size"]=pod_info.pod_size or pod_info.pod_size_compressed
 pod_config["available_resources"]=pod_info.persisted_resource_names
 return pod_config
def pull_state(pod_name,args,**kwargs):
 pre_config=kwargs.get("pre_config",wkueb)
 if not pod_name:
  raise wkueI("Need to specify a pod name")
 backend=CloudPodManager.get(pod_name=pod_name,pre_config=pre_config)
 backend.pull()
 print("Done.")
def list_pods(args):
 return PodConfigManager.list_pods()
def get_data_dir_from_container()->wkueD:
 try:
  details=run("%s inspect %s"%(config.DOCKER_CMD,config.MAIN_CONTAINER_NAME))
  details=json.loads(to_str(details))[0]
  mounts=details.get("Mounts")
  env=details.get("Config",{}).get("Env",[])
  data_dir_env=[e for e in env if e.startswith("DATA_DIR=")][0].partition("=")[2]
  try:
   data_dir_host=[m for m in mounts if m["Destination"]==data_dir_env][0]["Source"]
   data_dir_host=re.sub(r"^(/host_mnt)?",r"",data_dir_host)
   data_dir_env=data_dir_host
  except wkueI:
   LOG.debug(f"No docker volume for data dir '{data_dir_env}' detected")
  return data_dir_env
 except wkueI:
  LOG.warning('''Unable to determine DATA_DIR from LocalStack Docker container - please make sure $MAIN_CONTAINER_NAME is configured properly''')
def get_persisted_resource_names(data_dir)->List[wkueD]:
 names=[]
 with os.scandir(data_dir)as entries:
  for entry in entries:
   if entry.is_dir()and entry.name!="api_states":
    names.append(entry.name)
 with os.scandir(os.path.join(data_dir,"api_states"))as entries:
  for entry in entries:
   if entry.is_dir()and wkuec(os.listdir(entry.path))>0:
    names.append(entry.name)
 LOG.debug(f"Detected state files for the following APIs: {names}")
 return names
# Created by pyminifier (https://github.com/liftoff/pyminifier)
