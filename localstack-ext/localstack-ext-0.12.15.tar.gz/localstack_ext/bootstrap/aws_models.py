from localstack.utils.aws import aws_models
VRETk=super
VRETt=None
VRETd=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  VRETk(LambdaLayer,self).__init__(arn)
  self.cwd=VRETt
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.VRETd.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(RDSDatabase,self).__init__(VRETd,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(RDSCluster,self).__init__(VRETd,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(AppSyncAPI,self).__init__(VRETd,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(AmplifyApp,self).__init__(VRETd,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(ElastiCacheCluster,self).__init__(VRETd,env=env)
class TransferServer(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(TransferServer,self).__init__(VRETd,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(CloudFrontDistribution,self).__init__(VRETd,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,VRETd,env=VRETt):
  VRETk(CodeCommitRepository,self).__init__(VRETd,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
