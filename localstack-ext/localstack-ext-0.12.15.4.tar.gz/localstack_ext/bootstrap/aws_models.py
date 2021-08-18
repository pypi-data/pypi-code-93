from localstack.utils.aws import aws_models
GKAHx=super
GKAHe=None
GKAHR=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  GKAHx(LambdaLayer,self).__init__(arn)
  self.cwd=GKAHe
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.GKAHR.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(RDSDatabase,self).__init__(GKAHR,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(RDSCluster,self).__init__(GKAHR,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(AppSyncAPI,self).__init__(GKAHR,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(AmplifyApp,self).__init__(GKAHR,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(ElastiCacheCluster,self).__init__(GKAHR,env=env)
class TransferServer(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(TransferServer,self).__init__(GKAHR,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(CloudFrontDistribution,self).__init__(GKAHR,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,GKAHR,env=GKAHe):
  GKAHx(CodeCommitRepository,self).__init__(GKAHR,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
