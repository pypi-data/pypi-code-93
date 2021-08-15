import json
vsAtk=object
vsAtM=None
vsAtV=Exception
vsAty=set
vsAtK=property
vsAtD=classmethod
vsAtl=open
vsAtC=True
vsAtO=len
vsAto=getattr
vsAtR=type
vsAtJ=isinstance
vsAtP=list
vsAtI=False
import logging
import os
import re
from shutil import make_archive
import requests
import yaml
from dulwich import porcelain
from dulwich.client import get_transport_and_path_from_url
from dulwich.repo import Repo
from localstack import config
from localstack.constants import API_ENDPOINT
from localstack.utils.common import(chmod_r,clone,cp_r,disk_usage,download,format_number,in_docker,is_command_available,load_file,mkdir,new_tmp_file,retry,rm_rf,run,safe_requests,save_file,to_bytes,to_str,unzip)
from localstack.utils.testutil import create_zip_file
from localstack_ext.bootstrap.licensing import get_auth_headers
from localstack_ext.utils.pods import get_data_dir_from_container,get_persisted_resource_names
LOG=logging.getLogger(__name__)
PERSISTED_FOLDERS=["api_states","dynamodb","kinesis"]
class CloudPodManager(vsAtk):
 BACKEND="_none_"
 def __init__(self,pod_name=vsAtM,config=vsAtM):
  self.pod_name=pod_name
  self._pod_config=config
 def push(self):
  raise vsAtV("Not implemented")
 def pull(self):
  raise vsAtV("Not implemented")
 def get_pod_size(self):
  raise vsAtV("Not implemented")
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
   assert vsAty(statuses)==vsAty(["running"])
  retry(check_status,sleep=3,retries=10)
 @vsAtK
 def pod_config(self):
  return self._pod_config or PodConfigManager.pod_config(self.pod_name)
 @vsAtD
 def get(cls,pod_name,pre_config=vsAtM):
  pod_config=pre_config if pre_config else PodConfigManager.pod_config(pod_name)
  backend=pod_config.get("backend")
  for clazz in cls.__subclasses__():
   if clazz.BACKEND==backend:
    return clazz(pod_name=pod_name,config=pod_config)
  raise vsAtV('Unable to find Cloud Pod manager implementation type "%s"'%backend)
 @vsAtD
 def data_dir(cls):
  if not config.DATA_DIR or in_docker():
   config.DATA_DIR=get_data_dir_from_container()
  if not config.DATA_DIR:
   raise vsAtV("Working with local cloud pods requires $DATA_DIR configuration")
  return config.DATA_DIR
class CloudPodManagerFilesystem(CloudPodManager):
 BACKEND="file"
 def push(self):
  local_folder=self.target_folder()
  data_dir=self.data_dir()
  print('Pushing state of cloud pod "%s" to local folder: %s'%(self.pod_name,local_folder))
  mkdir(local_folder)
  mkdir(data_dir)
  cp_r(data_dir,local_folder)
  chmod_r(local_folder,0o777)
  print("Done.")
 def pull(self):
  local_folder=self.target_folder()
  if not os.path.exists(local_folder):
   print('WARN: Local path of cloud pod "%s" does not exist: %s'%(self.pod_name,local_folder))
   return
  print('Pulling state of cloud pod "%s" from local folder: %s'%(self.pod_name,local_folder))
  make_archive("datadir","zip",local_folder)
  with vsAtl("datadir.zip","rb")as fileobj:
   data=fileobj.read()
   headers={"x-localstack-request-url":f"{config.get_edge_url()}/_pods","x-localstack-edge":config.get_edge_url()}
   requests.post(f"{config.get_edge_url()}/_pods",headers=headers,data=data)
  rm_rf("datadir.zip")
 def target_folder(self):
  local_folder=re.sub(r"^file://","",self.pod_config.get("url",""))
  return local_folder
 def get_pod_size(self):
  target_folder=self.target_folder()
  return disk_usage(target_folder)
class CloudPodManagerManaged(CloudPodManager):
 BACKEND="managed"
 def push(self):
  presigned_url=self.presigned_url("push")
  data_dir=self.data_dir()
  zip_data_content=create_zip_file(data_dir,get_content=vsAtC)
  print('Pushing state of cloud pod "%s" to backend server (%s KB)'%(self.pod_name,format_number(vsAtO(zip_data_content)/1000.0)))
  res=safe_requests.put(presigned_url,data=zip_data_content)
  if res.status_code>=400:
   raise vsAtV("Unable to push pod state to API (code %s): %s"%(res.status_code,res.content))
  print("Done.")
 def pull(self):
  data_dir=self.data_dir()
  presigned_url=self.presigned_url("pull")
  print('Pulling state of cloud pod "%s" from managed storage'%self.pod_name)
  data_dir=self.data_dir()
  mkdir(data_dir)
  zip_path=new_tmp_file()
  download(presigned_url,zip_path)
  unzip(zip_path,data_dir)
  rm_rf(zip_path)
  self.restart_container()
 def presigned_url(self,mode):
  data={"pod_name":self.pod_name,"mode":mode}
  data=json.dumps(data)
  auth_headers=get_auth_headers()
  response=safe_requests.post("%s/cloudpods/data"%API_ENDPOINT,data,headers=auth_headers)
  content=response.content
  if response.status_code>=400:
   raise vsAtV("Unable to push cloud pod to API (code %s): %s"%(response.status_code,content))
  content=json.loads(to_str(content))
  return content["presignedURL"]
 def get_pod_size(self):
  data_dir=self.data_dir()
  return disk_usage(data_dir)
class CloudPodManagerGit(CloudPodManager):
 BACKEND="git"
 def push(self):
  repo=self.local_repo()
  client,path=self.client()
  branch=to_bytes(self.pod_config.get("branch"))
  remote_location=self.pod_config.get("url")
  try:
   porcelain.pull(repo,remote_location,refspecs=branch)
  except vsAtV as e:
   LOG.info("Unable to pull repo: %s"%e)
  is_empty_repo=b"HEAD" not in repo or repo.refs.allkeys()==vsAty([b"HEAD"])
  if is_empty_repo:
   LOG.debug("Initializing empty repository %s"%self.clone_dir)
   init_file=os.path.join(self.clone_dir,".init")
   save_file(init_file,"")
   porcelain.add(repo,init_file)
   porcelain.commit(repo,message="Initial commit")
  if branch not in repo:
   porcelain.branch_create(repo,branch,force=vsAtC)
  self.switch_branch(branch)
  for folder in PERSISTED_FOLDERS:
   LOG.info("Copying persistence folder %s to local git repo %s"%(folder,self.clone_dir))
   src_folder=os.path.join(self.data_dir(),folder)
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
   raise vsAtV('Unable to find branch "%s" in remote git repo'%branch)
  remote_location=self.pod_config.get("url")
  self.switch_branch(branch)
  branch_ref=b"refs/heads/%s"%to_bytes(branch)
  from dulwich.errors import HangupException
  try:
   porcelain.pull(repo,remote_location,branch_ref)
  except HangupException:
   pass
  for folder in PERSISTED_FOLDERS:
   src_folder=os.path.join(self.clone_dir,folder)
   tgt_folder=os.path.join(self.data_dir(),folder)
   cp_r(src_folder,tgt_folder,rm_dest_on_conflict=vsAtC)
  self.restart_container()
 def client(self):
  client,path=get_transport_and_path_from_url(self.pod_config.get("url"))
  return client,path
 def local_repo(self):
  self.clone_dir=vsAto(self,"clone_dir",vsAtM)
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
 def get_pod_size(self):
  self.local_repo()
  return disk_usage(self.clone_dir)
class PodConfigManagerMeta(vsAtR):
 def __getattr__(cls,attr):
  def _call(*args,**kwargs):
   result=vsAtM
   for manager in cls.CHAIN:
    try:
     tmp=vsAto(manager,attr)(*args,**kwargs)
     if tmp:
      if not result:
       result=tmp
      elif vsAtJ(tmp,vsAtP)and vsAtJ(result,vsAtP):
       result.extend(tmp)
    except vsAtV:
     pass
   if result is not vsAtM:
    return result
   raise vsAtV('Unable to run operation "%s" for local or remote configuration'%attr)
  return _call
class PodConfigManager(vsAtk,metaclass=PodConfigManagerMeta):
 CHAIN=[]
 @vsAtD
 def pod_config(cls,pod_name):
  pods=PodConfigManager.list_pods()
  pod_config=[pod for pod in pods if pod["pod_name"]==pod_name]
  if not pod_config:
   raise vsAtV('Unable to find config for pod named "%s"'%pod_name)
  return pod_config[0]
class PodConfigManagerLocal(vsAtk):
 CONFIG_FILE=".localstack.yml"
 def list_pods(self):
  local_pods=self._load_config(safe=vsAtC).get("pods",{})
  local_pods=[{"pod_name":k,"state":"Local Only",**v}for k,v in local_pods.items()]
  existing_names=vsAty([pod["pod_name"]for pod in local_pods])
  result=[pod for pod in local_pods if pod["pod_name"]not in existing_names]
  return result
 def store_pod_metadata(self,pod_name,metadata):
  pass
 def _load_config(self,safe=vsAtI):
  try:
   return yaml.load(to_str(load_file(self.CONFIG_FILE)))
  except vsAtV:
   if safe:
    return{}
   raise vsAtV('Unable to find and parse config file "%s"'%self.CONFIG_FILE)
class PodConfigManagerRemote(vsAtk):
 def list_pods(self):
  result=[]
  auth_headers=get_auth_headers()
  response=safe_requests.get("%s/cloudpods"%API_ENDPOINT,headers=auth_headers)
  content=response.content
  if response.status_code>=400:
   raise vsAtV("Unable to fetch list of pods from API (code %s): %s"%(response.status_code,content))
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
   raise vsAtV("Unable to store pod metadata in API (code %s): %s"%(response.status_code,content))
  return json.loads(to_str(content))
PodConfigManager.CHAIN.append(PodConfigManagerLocal())
PodConfigManager.CHAIN.append(PodConfigManagerRemote())
def push_state(pod_name,args,**kwargs):
 pre_config=kwargs.get("pre_config",vsAtM)
 backend=CloudPodManager.get(pod_name=pod_name,pre_config=pre_config)
 pod_config=clone(backend.pod_config)
 pod_config["size"]=backend.get_pod_size()
 pod_config["available_resources"]=get_persisted_resource_names()
 backend.push()
 return pod_config
def pull_state(pod_name,args,**kwargs):
 pre_config=kwargs.get("pre_config",vsAtM)
 if not pod_name:
  raise vsAtV("Need to specify a pod name")
 backend=CloudPodManager.get(pod_name=pod_name,pre_config=pre_config)
 backend.pull()
def list_pods(args):
 return PodConfigManager.list_pods()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
