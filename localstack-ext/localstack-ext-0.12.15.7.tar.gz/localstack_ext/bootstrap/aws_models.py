from localstack.utils.aws import aws_models
MmEQK=super
MmEQY=None
MmEQh=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  MmEQK(LambdaLayer,self).__init__(arn)
  self.cwd=MmEQY
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.MmEQh.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(RDSDatabase,self).__init__(MmEQh,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(RDSCluster,self).__init__(MmEQh,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(AppSyncAPI,self).__init__(MmEQh,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(AmplifyApp,self).__init__(MmEQh,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(ElastiCacheCluster,self).__init__(MmEQh,env=env)
class TransferServer(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(TransferServer,self).__init__(MmEQh,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(CloudFrontDistribution,self).__init__(MmEQh,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,MmEQh,env=MmEQY):
  MmEQK(CodeCommitRepository,self).__init__(MmEQh,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
