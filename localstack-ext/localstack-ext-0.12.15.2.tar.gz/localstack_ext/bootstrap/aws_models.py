from localstack.utils.aws import aws_models
FnWxm=super
FnWxc=None
FnWxX=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  FnWxm(LambdaLayer,self).__init__(arn)
  self.cwd=FnWxc
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.FnWxX.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(RDSDatabase,self).__init__(FnWxX,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(RDSCluster,self).__init__(FnWxX,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(AppSyncAPI,self).__init__(FnWxX,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(AmplifyApp,self).__init__(FnWxX,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(ElastiCacheCluster,self).__init__(FnWxX,env=env)
class TransferServer(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(TransferServer,self).__init__(FnWxX,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(CloudFrontDistribution,self).__init__(FnWxX,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,FnWxX,env=FnWxc):
  FnWxm(CodeCommitRepository,self).__init__(FnWxX,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
