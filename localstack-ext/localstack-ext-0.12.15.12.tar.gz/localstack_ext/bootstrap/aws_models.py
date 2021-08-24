from localstack.utils.aws import aws_models
vWNXz=super
vWNXR=None
vWNXM=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  vWNXz(LambdaLayer,self).__init__(arn)
  self.cwd=vWNXR
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.vWNXM.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(RDSDatabase,self).__init__(vWNXM,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(RDSCluster,self).__init__(vWNXM,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(AppSyncAPI,self).__init__(vWNXM,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(AmplifyApp,self).__init__(vWNXM,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(ElastiCacheCluster,self).__init__(vWNXM,env=env)
class TransferServer(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(TransferServer,self).__init__(vWNXM,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(CloudFrontDistribution,self).__init__(vWNXM,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,vWNXM,env=vWNXR):
  vWNXz(CodeCommitRepository,self).__init__(vWNXM,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
