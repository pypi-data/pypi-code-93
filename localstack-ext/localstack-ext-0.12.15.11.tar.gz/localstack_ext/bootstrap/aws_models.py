from localstack.utils.aws import aws_models
LgDJh=super
LgDJw=None
LgDJA=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  LgDJh(LambdaLayer,self).__init__(arn)
  self.cwd=LgDJw
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.LgDJA.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(RDSDatabase,self).__init__(LgDJA,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(RDSCluster,self).__init__(LgDJA,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(AppSyncAPI,self).__init__(LgDJA,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(AmplifyApp,self).__init__(LgDJA,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(ElastiCacheCluster,self).__init__(LgDJA,env=env)
class TransferServer(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(TransferServer,self).__init__(LgDJA,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(CloudFrontDistribution,self).__init__(LgDJA,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,LgDJA,env=LgDJw):
  LgDJh(CodeCommitRepository,self).__init__(LgDJA,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
