import logging
geRit=Exception
geRiE=any
geRiV=str
geRiL=None
geRix=False
geRih=bool
geRiT=True
import os
import traceback
from localstack import config as localstack_config
from localstack.constants import LOCALSTACK_INFRA_PROCESS,LOCALSTACK_WEB_PROCESS,TRUE_STRINGS
from localstack.utils import common
from localstack.utils.bootstrap import API_DEPENDENCIES,is_api_enabled
from localstack_ext import config as config_ext
from localstack_ext.bootstrap import cli,install,licensing,local_daemon
LOG=logging.getLogger(__name__)
EXTERNAL_PORT_APIS=("apigateway","apigatewayv2","athena","cloudfront","codecommit","ecs","ecr","elasticache","mediastore","rds","transfer","kafka","neptune","azure")
def register_localstack_plugins():
 _setup_logging()
 is_infra_process=os.environ.get(LOCALSTACK_INFRA_PROCESS)in TRUE_STRINGS
 is_api_key_configured=api_key_configured()
 if is_infra_process:
  install.install_libs()
  if is_api_key_configured:
   install.setup_ssl_cert()
 if os.environ.get(LOCALSTACK_WEB_PROCESS):
  return{}
 with licensing.prepare_environment():
  try:
   from localstack_ext.services import dns_server
   dns_server.setup_network_configuration()
  except geRit:
   return
  if is_infra_process:
   load_plugin_files()
  try:
   if is_api_key_configured and not is_infra_process and is_api_enabled("ec2"):
    local_daemon.start_in_background()
  except geRit as e:
   LOG.warning("Unable to start local daemon process: %s"%e)
  if is_api_key_configured:
   if os.environ.get("EDGE_PORT")and not localstack_config.EDGE_PORT_HTTP:
    LOG.warning(("!! Configuring EDGE_PORT={p} without setting EDGE_PORT_HTTP may lead "+"to issues; better leave the defaults, or set EDGE_PORT=443 and EDGE_PORT_HTTP={p}").format(p=localstack_config.EDGE_PORT))
   else:
    port=localstack_config.EDGE_PORT
    localstack_config.EDGE_PORT=443
    localstack_config.EDGE_PORT_HTTP=port
 API_DEPENDENCIES["amplify"]=["s3","appsync","cognito-idp","cognito-identity"]
 API_DEPENDENCIES["apigateway"]=["apigatewayv2"]
 API_DEPENDENCIES["athena"]=["emr"]
 API_DEPENDENCIES["docdb"]=["rds"]
 API_DEPENDENCIES["ecs"]=["ecr"]
 API_DEPENDENCIES["elasticache"]=["ec2"]
 API_DEPENDENCIES["elb"]=["elbv2"]
 API_DEPENDENCIES["emr"]=["athena","s3"]
 API_DEPENDENCIES["glacier"]=["s3"]
 API_DEPENDENCIES["glue"]=["rds"]
 API_DEPENDENCIES["iot"]=["iotanalytics","iot-data","iotwireless"]
 API_DEPENDENCIES["kinesisanalytics"]=["kinesis","dynamodb"]
 API_DEPENDENCIES["neptune"]=["rds"]
 API_DEPENDENCIES["rds"]=["rds-data"]
 API_DEPENDENCIES["redshift"]=["redshift-data"]
 API_DEPENDENCIES["timestream"]=["timestream-write","timestream-query"]
 API_DEPENDENCIES["transfer"]=["s3"]
 docker_flags=[]
 if config_ext.use_custom_dns():
  if not common.is_port_open(dns_server.DNS_PORT,protocols="tcp"):
   docker_flags+=["-p {a}:{p}:{p}".format(a=config_ext.DNS_ADDRESS,p=dns_server.DNS_PORT)]
  if not common.is_port_open(dns_server.DNS_PORT,protocols="udp"):
   docker_flags+=["-p {a}:{p}:{p}/udp".format(a=config_ext.DNS_ADDRESS,p=dns_server.DNS_PORT)]
 if geRiE([is_api_enabled(api)for api in EXTERNAL_PORT_APIS]):
  docker_flags+=["-p {start}-{end}:{start}-{end}".format(start=config_ext.SERVICE_INSTANCES_PORTS_START,end=config_ext.SERVICE_INSTANCES_PORTS_END)]
 if is_api_enabled("eks"):
  kube_config=os.path.expanduser("~/.kube/config")
  if os.path.exists(kube_config):
   docker_flags+=["-v %s:/root/.kube/config"%kube_config]
 if is_api_enabled("azure"):
  docker_flags+=["-p {port}:{port}".format(port=5671)]
 if os.environ.get("AZURE"):
  docker_flags+=["-p {p}:{p}".format(p=config_ext.PORT_AZURE)]
 result={"docker":{"run_flags":" ".join(docker_flags)}}
 return result
def load_plugin_files():
 try:
  from localstack.services.plugins import Plugin,register_plugin
  from localstack_ext.bootstrap.dashboard import dashboard_extended
  from localstack_ext.services import edge
  from localstack_ext.services.amplify import amplify_starter
  from localstack_ext.services.apigateway import apigateway_extended
  from localstack_ext.services.appconfig import appconfig_starter
  from localstack_ext.services.applicationautoscaling import(applicationautoscaling_listener,applicationautoscaling_starter)
  from localstack_ext.services.appsync import appsync_starter
  from localstack_ext.services.athena import athena_starter
  from localstack_ext.services.autoscaling import autoscaling_starter
  from localstack_ext.services.awslambda import lambda_extended
  from localstack_ext.services.azure import azure_starter
  from localstack_ext.services.backup import backup_starter
  from localstack_ext.services.batch import batch_listener,batch_starter
  from localstack_ext.services.cloudformation import cloudformation_extended
  from localstack_ext.services.cloudfront import cloudfront_starter
  from localstack_ext.services.cloudtrail import cloudtrail_starter
  from localstack_ext.services.codecommit import codecommit_listener,codecommit_starter
  from localstack_ext.services.cognito import(cognito_identity_api,cognito_idp_api,cognito_starter)
  from localstack_ext.services.costexplorer import costexplorer_starter
  from localstack_ext.services.docdb import docdb_api
  from localstack_ext.services.dynamodb import dynamodb_extended
  from localstack_ext.services.ec2 import ec2_listener,ec2_starter
  from localstack_ext.services.ecr import ecr_listener,ecr_starter
  from localstack_ext.services.ecs import ecs_listener,ecs_starter
  from localstack_ext.services.efs import efs_api
  from localstack_ext.services.eks import eks_starter
  from localstack_ext.services.elasticache import elasticache_starter
  from localstack_ext.services.elasticbeanstalk import elasticbeanstalk_starter
  from localstack_ext.services.elb import elb_listener,elb_starter
  from localstack_ext.services.emr import emr_listener,emr_starter
  from localstack_ext.services.events import events_extended
  from localstack_ext.services.glacier import glacier_listener,glacier_starter
  from localstack_ext.services.glue import glue_listener,glue_starter
  from localstack_ext.services.iam import iam_extended
  from localstack_ext.services.iot import iot_listener,iot_starter
  from localstack_ext.services.kafka import kafka_starter
  from localstack_ext.services.kinesisanalytics import kinesis_analytics_api
  from localstack_ext.services.lakeformation import lakeformation_api
  from localstack_ext.services.mediastore import mediastore_starter
  from localstack_ext.services.neptune import neptune_api
  from localstack_ext.services.organizations import organizations_starter
  from localstack_ext.services.qldb import qldb_starter
  from localstack_ext.services.rds import rds_listener,rds_starter
  from localstack_ext.services.redshift import redshift_listener,redshift_starter
  from localstack_ext.services.route53 import route53_extended
  from localstack_ext.services.s3 import s3_extended
  from localstack_ext.services.sagemaker import sagemaker_starter
  from localstack_ext.services.secretsmanager import secretsmanager_extended
  from localstack_ext.services.serverlessrepo import serverlessrepo_starter
  from localstack_ext.services.servicediscovery import servicediscovery_starter
  from localstack_ext.services.ses import ses_extended
  from localstack_ext.services.sns import sns_extended
  from localstack_ext.services.sqs import sqs_extended
  from localstack_ext.services.stepfunctions import stepfunctions_extended
  from localstack_ext.services.sts import sts_extended
  from localstack_ext.services.timestream import timestream_starter
  from localstack_ext.services.transfer import transfer_starter
  from localstack_ext.services.xray import xray_listener,xray_starter
  from localstack_ext.utils import persistence as persistence_ext
  register_plugin(Plugin("amplify",start=amplify_starter.start_amplify))
  register_plugin(Plugin("appconfig",start=appconfig_starter.start_appconfig))
  register_plugin(Plugin("application-autoscaling",start=applicationautoscaling_starter.start_applicationautoscaling,listener=applicationautoscaling_listener.UPDATE_APPLICATION_AUTOSCALING))
  register_plugin(Plugin("appsync",start=appsync_starter.start_appsync))
  register_plugin(Plugin("athena",start=athena_starter.start_athena))
  register_plugin(Plugin("autoscaling",start=autoscaling_starter.start_autoscaling))
  register_plugin(Plugin("azure",start=azure_starter.start_azure))
  register_plugin(Plugin("backup",start=backup_starter.start_backup))
  register_plugin(Plugin("batch",start=batch_starter.start_batch,listener=batch_listener.UPDATE_BATCH))
  register_plugin(Plugin("ce",start=costexplorer_starter.start_costexplorer))
  register_plugin(Plugin("cloudfront",start=cloudfront_starter.start_cloudfront))
  register_plugin(Plugin("cloudtrail",start=cloudtrail_starter.start_cloudtrail))
  register_plugin(Plugin("codecommit",start=codecommit_starter.start_codecommit,listener=codecommit_listener.UPDATE_CODECOMMIT))
  register_plugin(Plugin("cognito-identity",start=cognito_starter.start_cognito_identity,listener=cognito_identity_api.UPDATE_COGNITO_IDENTITY))
  register_plugin(Plugin("cognito-idp",start=cognito_starter.start_cognito_idp,listener=cognito_idp_api.UPDATE_COGNITO))
  register_plugin(Plugin("docdb",start=docdb_api.start_docdb))
  register_plugin(Plugin("ec2",start=ec2_starter.start_ec2,listener=ec2_listener.UPDATE_EC2,priority=10))
  register_plugin(Plugin("ecr",start=ecr_starter.start_ecr,listener=ecr_listener.UPDATE_ECR))
  register_plugin(Plugin("ecs",start=ecs_starter.start_ecs,listener=ecs_listener.UPDATE_ECS))
  register_plugin(Plugin("efs",start=efs_api.start_efs))
  register_plugin(Plugin("elasticache",start=elasticache_starter.start_elasticache))
  register_plugin(Plugin("elasticbeanstalk",start=elasticbeanstalk_starter.start_elasticbeanstalk))
  register_plugin(Plugin("elb",start=elb_starter.start_elb,listener=elb_listener.UPDATE_ELB))
  register_plugin(Plugin("elbv2",start=elb_starter.start_elbv2,listener=elb_listener.UPDATE_ELB))
  register_plugin(Plugin("eks",start=eks_starter.start_eks))
  register_plugin(Plugin("emr",start=emr_starter.start_emr,listener=emr_listener.UPDATE_EMR))
  register_plugin(Plugin("glacier",start=glacier_starter.start_glacier,listener=glacier_listener.UPDATE_GLACIER))
  register_plugin(Plugin("glue",start=glue_starter.start_glue,listener=glue_listener.UPDATE_GLUE))
  register_plugin(Plugin("iot",start=iot_starter.start_iot,listener=iot_listener.UPDATE_IOT))
  register_plugin(Plugin("kafka",start=kafka_starter.start_kafka))
  register_plugin(Plugin("kinesisanalytics",start=kinesis_analytics_api.start_kinesis_analytics))
  register_plugin(Plugin("lakeformation",start=lakeformation_api.start_lakeformation))
  register_plugin(Plugin("mediastore",start=mediastore_starter.start_mediastore))
  register_plugin(Plugin("neptune",start=neptune_api.start_neptune))
  register_plugin(Plugin("organizations",start=organizations_starter.start_organizations))
  register_plugin(Plugin("qldb",start=qldb_starter.start_qldb))
  register_plugin(Plugin("rds",start=rds_starter.start_rds,listener=rds_listener.UPDATE_RDS))
  register_plugin(Plugin("redshift",start=redshift_starter.start_redshift,listener=redshift_listener.UPDATE_REDSHIFT,priority=10))
  register_plugin(Plugin("sagemaker",start=sagemaker_starter.start_sagemaker))
  register_plugin(Plugin("serverlessrepo",start=serverlessrepo_starter.start_serverlessrepo))
  register_plugin(Plugin("servicediscovery",start=servicediscovery_starter.start_servicediscovery))
  register_plugin(Plugin("timestream",start=timestream_starter.start_timestream))
  register_plugin(Plugin("transfer",start=transfer_starter.start_transfer))
  register_plugin(Plugin("xray",start=xray_starter.start_xray,listener=xray_listener.UPDATE_XRAY))
  persistence_ext.enable_extended_persistence()
  lambda_extended.patch_lambda()
  sns_extended.patch_sns()
  sqs_extended.patch_sqs()
  apigateway_extended.patch_apigateway()
  cloudformation_extended.patch_cloudformation()
  stepfunctions_extended.patch_stepfunctions()
  s3_extended.patch_s3()
  iam_extended.patch_iam()
  dynamodb_extended.patch_dynamodb()
  events_extended.patch_events()
  secretsmanager_extended.patch_secretsmanager()
  sts_extended.patch_sts()
  ses_extended.patch_ses()
  route53_extended.patch_route53()
  dashboard_extended.patch_dashboard()
  edge.patch_start_edge()
  patch_start_infra()
 except geRit as e:
  if "No module named" not in geRiV(e):
   print("ERROR: %s %s"%(e,traceback.format_exc()))
def patch_start_infra():
 from localstack.services import infra
 try:
  from localstack_ext.utils.aws.metadata_service import start_metadata_service
 except geRit:
  start_metadata_service=geRiL
 def do_start_infra(asynchronous,apis,is_in_docker,*args,**kwargs):
  if common.in_docker():
   try:
    start_metadata_service and start_metadata_service()
   except geRit:
    pass
  enforce_before=config_ext.ENFORCE_IAM
  try:
   config_ext.ENFORCE_IAM=geRix
   return do_start_infra_orig(asynchronous,apis,is_in_docker,*args,**kwargs)
  finally:
   config_ext.ENFORCE_IAM=enforce_before
 do_start_infra_orig=infra.do_start_infra
 infra.do_start_infra=do_start_infra
def _setup_logging():
 log_level=logging.DEBUG if localstack_config.DEBUG else logging.INFO
 logging.getLogger("localstack_ext").setLevel(log_level)
 logging.getLogger("botocore").setLevel(logging.INFO)
 logging.getLogger("kubernetes").setLevel(logging.INFO)
 logging.getLogger("pyftpdlib").setLevel(logging.INFO)
 logging.getLogger("pyhive").setLevel(logging.INFO)
 logging.getLogger("websockets").setLevel(logging.INFO)
 logging.getLogger("asyncio").setLevel(logging.INFO)
 logging.getLogger("hpack").setLevel(logging.INFO)
 logging.getLogger("jnius.reflect").setLevel(logging.INFO)
 logging.getLogger("dulwich").setLevel(logging.ERROR)
 logging.getLogger("postgresql_proxy").setLevel(logging.WARNING)
 logging.getLogger("intercept").setLevel(logging.WARNING)
 logging.getLogger("root").setLevel(logging.WARNING)
 logging.getLogger("").setLevel(logging.WARNING)
def api_key_configured():
 return geRih(os.environ.get("LOCALSTACK_API_KEY"))
def register_localstack_commands():
 if api_key_configured():
  cli.register_commands()
 return geRiT
# Created by pyminifier (https://github.com/liftoff/pyminifier)
