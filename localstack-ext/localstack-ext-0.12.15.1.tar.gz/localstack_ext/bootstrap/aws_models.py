from localstack.utils.aws import aws_models
gprGL=super
gprGO=None
gprGA=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  gprGL(LambdaLayer,self).__init__(arn)
  self.cwd=gprGO
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.gprGA.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(RDSDatabase,self).__init__(gprGA,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(RDSCluster,self).__init__(gprGA,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(AppSyncAPI,self).__init__(gprGA,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(AmplifyApp,self).__init__(gprGA,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(ElastiCacheCluster,self).__init__(gprGA,env=env)
class TransferServer(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(TransferServer,self).__init__(gprGA,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(CloudFrontDistribution,self).__init__(gprGA,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,gprGA,env=gprGO):
  gprGL(CodeCommitRepository,self).__init__(gprGA,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
