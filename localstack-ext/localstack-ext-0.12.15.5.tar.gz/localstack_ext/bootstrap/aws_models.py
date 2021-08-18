from localstack.utils.aws import aws_models
BFpLz=super
BFpLY=None
BFpLm=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  BFpLz(LambdaLayer,self).__init__(arn)
  self.cwd=BFpLY
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.BFpLm.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(RDSDatabase,self).__init__(BFpLm,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(RDSCluster,self).__init__(BFpLm,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(AppSyncAPI,self).__init__(BFpLm,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(AmplifyApp,self).__init__(BFpLm,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(ElastiCacheCluster,self).__init__(BFpLm,env=env)
class TransferServer(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(TransferServer,self).__init__(BFpLm,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(CloudFrontDistribution,self).__init__(BFpLm,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,BFpLm,env=BFpLY):
  BFpLz(CodeCommitRepository,self).__init__(BFpLm,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
