from localstack.utils.aws import aws_models
ntyAk=super
ntyAJ=None
ntyAQ=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  ntyAk(LambdaLayer,self).__init__(arn)
  self.cwd=ntyAJ
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.ntyAQ.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(RDSDatabase,self).__init__(ntyAQ,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(RDSCluster,self).__init__(ntyAQ,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(AppSyncAPI,self).__init__(ntyAQ,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(AmplifyApp,self).__init__(ntyAQ,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(ElastiCacheCluster,self).__init__(ntyAQ,env=env)
class TransferServer(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(TransferServer,self).__init__(ntyAQ,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(CloudFrontDistribution,self).__init__(ntyAQ,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,ntyAQ,env=ntyAJ):
  ntyAk(CodeCommitRepository,self).__init__(ntyAQ,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
