from localstack.utils.aws import aws_models
ynure=super
ynurc=None
ynurB=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  ynure(LambdaLayer,self).__init__(arn)
  self.cwd=ynurc
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.ynurB.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(RDSDatabase,self).__init__(ynurB,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(RDSCluster,self).__init__(ynurB,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(AppSyncAPI,self).__init__(ynurB,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(AmplifyApp,self).__init__(ynurB,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(ElastiCacheCluster,self).__init__(ynurB,env=env)
class TransferServer(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(TransferServer,self).__init__(ynurB,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(CloudFrontDistribution,self).__init__(ynurB,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,ynurB,env=ynurc):
  ynure(CodeCommitRepository,self).__init__(ynurB,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
