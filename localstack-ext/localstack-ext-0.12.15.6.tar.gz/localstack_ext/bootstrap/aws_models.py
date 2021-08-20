from localstack.utils.aws import aws_models
TCsMH=super
TCsMm=None
TCsMY=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  TCsMH(LambdaLayer,self).__init__(arn)
  self.cwd=TCsMm
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.TCsMY.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(RDSDatabase,self).__init__(TCsMY,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(RDSCluster,self).__init__(TCsMY,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(AppSyncAPI,self).__init__(TCsMY,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(AmplifyApp,self).__init__(TCsMY,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(ElastiCacheCluster,self).__init__(TCsMY,env=env)
class TransferServer(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(TransferServer,self).__init__(TCsMY,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(CloudFrontDistribution,self).__init__(TCsMY,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,TCsMY,env=TCsMm):
  TCsMH(CodeCommitRepository,self).__init__(TCsMY,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
