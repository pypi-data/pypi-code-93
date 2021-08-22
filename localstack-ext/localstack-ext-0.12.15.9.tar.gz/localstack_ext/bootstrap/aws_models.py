from localstack.utils.aws import aws_models
scKFG=super
scKFE=None
scKFB=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  scKFG(LambdaLayer,self).__init__(arn)
  self.cwd=scKFE
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.scKFB.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(RDSDatabase,self).__init__(scKFB,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(RDSCluster,self).__init__(scKFB,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(AppSyncAPI,self).__init__(scKFB,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(AmplifyApp,self).__init__(scKFB,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(ElastiCacheCluster,self).__init__(scKFB,env=env)
class TransferServer(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(TransferServer,self).__init__(scKFB,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(CloudFrontDistribution,self).__init__(scKFB,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,scKFB,env=scKFE):
  scKFG(CodeCommitRepository,self).__init__(scKFB,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
