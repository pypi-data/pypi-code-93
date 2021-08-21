from localstack.utils.aws import aws_models
VgaXR=super
VgaXN=None
VgaXB=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  VgaXR(LambdaLayer,self).__init__(arn)
  self.cwd=VgaXN
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.VgaXB.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(RDSDatabase,self).__init__(VgaXB,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(RDSCluster,self).__init__(VgaXB,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(AppSyncAPI,self).__init__(VgaXB,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(AmplifyApp,self).__init__(VgaXB,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(ElastiCacheCluster,self).__init__(VgaXB,env=env)
class TransferServer(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(TransferServer,self).__init__(VgaXB,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(CloudFrontDistribution,self).__init__(VgaXB,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,VgaXB,env=VgaXN):
  VgaXR(CodeCommitRepository,self).__init__(VgaXB,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
