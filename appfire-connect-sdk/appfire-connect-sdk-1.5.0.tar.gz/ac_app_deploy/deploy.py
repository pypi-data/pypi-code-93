#
#  Copyright (c) 2020 Appfire Technologies, Inc.
#  All rights reserved.
#  This software is licensed under the provisions of the "Bob Swift Atlassian Add-ons EULA"
#  (https://bobswift.atlassian.net/wiki/x/WoDXBQ) as well as under the provisions of
#  the "Standard EULA" from the "Atlassian Marketplace Terms of Use" as a "Marketplace Product”
#  (http://www.atlassian.com/licensing/marketplace/termsofuse).
#  See the LICENSE file for more details.
#

import json
import coloredlogs,logging
import subprocess
import sys
import click
import yaml
import os
from importlib.metadata import version
from pyngrok import conf, ngrok
import requests
import shutil
import questionary
from subprocess import PIPE

def getVersion():
    return version('appfire-connect-sdk')

service_modules = ["ac-core", "ac-allowlist", "ac-automation", "ac-macro-security", "ac-migrations", "ac-proxy", "ac-utils"]

@click.command()
@click.option('--verbose', '-v', is_flag=True, help="Verbose output")
@click.option('--profile', '-p', help="AWS profile as the default environment")
@click.option('--env', '-e', help="standalone, dts or prod", default="standalone")
@click.option('--stack', '-s', help="CDK stack to deploy", default="app")
@click.option('--stage', '-stage', help="dev, test, stage or prod", default="dev")
@click.option('--app-suffix', '-as', help="blue or green", default="blue")
@click.option('--build','-b',help="True or False",default=True)
@click.option('--api-domain','-api-domain',help="API domain for Core Services(common.appfire.app or dts.common.appfire.app or services.custom-domain)")
@click.option('--api-stage','-api-stage',help="API stage for Core Services(prod or snapshot or stage)")
@click.option('--app-api-domain','-app-api-domain',help="API domain for App Services")
@click.option('--require-approval','-require-approval',help="never or any-change or broadening",default="never")
@click.option('--tag','-t',help="service module image tag",default="latest")
@click.option('--bitbucket-username', '-bb-un', help="Bitbucket username")
@click.option('--bitbucket-password', '-bb-pwd', help="Bitbucket password")
@click.option('--bitbucket-branch', '-bb-branch', help="Bitbucket branch for custom pipeline to run against", default="develop")
@click.option('--bitbucket-tag-value', '-bb-tag-value', help="Tag value for Docker image for pipeline run")
@click.option('--aws-home', '-aws-home', help="AWS home directory for config/credentials", default="~/.aws")
@click.option('--disable-clone-prompt', '-disable-clone-prompt', help="Disable prompt for git clone.", default="True")
@click.option('--version','-v', help="Specify App version", default="")
@click.argument('command')
@click.help_option("--help", "-h")
def process(verbose, command, profile, env, stage, stack, app_suffix, build, api_domain, api_stage, app_api_domain, require_approval, tag, bitbucket_username, bitbucket_password, bitbucket_branch, bitbucket_tag_value, aws_home, disable_clone_prompt, version):
    """
    Gathers information related to deployment and deploys the CDK stack

    \b
    Commands:
      bootstrap     Bootstrap the CDK toolkit
      build         Build the app
        Options:  --profile, --env, --stage, --stack, --api-domain, --api-stage
      build:dev     Build the app with webpack-dev.config.js config
        Options:  --profile, --env, --stage, --stack, --api-domain, --api-stage
      deploy        Build and deploy the specified stack
        Options:  --profile, --stack, --tag, --aws-home
      diff          Diff the local stack with deployed stack
        Options:  --profile
      docker-build  Docker build the service module and push image to AWS DTS ECR
        Options:  --tag
      dts-ecr-login Docker login for AWS DTS Elastic Container Registry (ECR), use --profile for AWS DTS profile
        Options: --profile
      synth         Generates AWS CloudFormation template from the app
        Options:  --profile
      destroy       Destroy the specified stack
        Options:  --profile, --stack
      list          List the stacks for the app
        Options:  --profile
      list-stacks   List the available stacks for deployment
      list-tags     List the Docker tags for a service module, use --profile for AWS DTS
        Options:  --profile, --stack
      run           Build and run the app with webpack-dev.config.js config
        Options:  --profile, --env, --stage, --stack, --api-domain, --api-stage, --app-api-domain
      run-pipeline  Run a Bitbucket pipeline for a service module
        Options:  --stack, --bitbucket-username, --bitbucket-password, --bitbucket-branch, --bitbucket-tag-value
      version       Print version information for the Appfire SDK

    Learn more - https://wiki.appfire.com/x/x6gjCQ

    Documentation - https://appfire.bitbucket.io/

    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, stream=sys.stdout, format="%(message)s")
    logger = logging.getLogger("ac_app_deploy")
    coloredlogs.install(level='DEBUG',logger=logger)

    if command.lower() == 'version':
        print("Appfire Connect SDK version " + getVersion())
        return
    if command.lower() == 'dts-ecr-login':
        dts_ecr_login(logger,profile)
        return
    if command.lower() == 'list-tags':
        list_tags(logger,profile,stack)
        return
    if command.lower() == 'list-stacks':
        list_stacks(logger)
        return
    if command.lower() == 'run-pipeline':
        run_pipeline(logger,stack,bitbucket_username,bitbucket_password,bitbucket_branch,bitbucket_tag_value)
        return
    if command.lower() == 'docker-build':
        docker_build(logger,tag,disable_clone_prompt)
        return
    
    logger.debug("checking environment " + env)
    if env == 'standalone':
        personal_env_settings = None
        try:
            with open("./personal.env.yml", 'r') as stream:
                personal_env_settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.info(exc)
        except IOError:
            logger.info("personal.env.yml not found!")
            sys.exit(1)

        if 'ngrok_auth_token' in personal_env_settings.keys():
            token = personal_env_settings['environment']['personal']['ngrok_auth_token']
        else:
            token=""
        aws_profile = profile if profile else personal_env_settings['environment']['personal'].get('profile')
        domain = personal_env_settings['environment']['personal']['domain']
        ### since stage cli arg has default value the yml val will never be picked but for standalone case it makes more sense to have this from personal.env.yml
        stage = personal_env_settings['environment']['personal']['stage'] if personal_env_settings['environment']['personal']['stage'] else stage
        log_info(logger, aws_profile, domain, env)
        ### Check if CDK_DEPLOY_ACCOUNT and CDK_DEPLOY_REGION exist in personal.env.yml
        if personal_env_settings['environment']['personal']['CDK_DEPLOY_ACCOUNT'] and personal_env_settings['environment']['personal']['CDK_DEPLOY_REGION'] :
            #### Setting env varibale CDK_DEPLOY_ACCOUNT and CDK_DEPLOY_REGION for standalone deployment
            logger.info("Setting up Env variables : CDK_DEPLOY_ACCOUNT {}, CDK_DEPLOY_REGION {}".format(personal_env_settings['environment']['personal']['CDK_DEPLOY_ACCOUNT'],personal_env_settings['environment']['personal']['CDK_DEPLOY_REGION']))
            os.environ["CDK_DEPLOY_ACCOUNT"] = str(personal_env_settings['environment']['personal']['CDK_DEPLOY_ACCOUNT'])
            os.environ["CDK_DEPLOY_REGION"] = personal_env_settings['environment']['personal']['CDK_DEPLOY_REGION']
        else :
            logger.info("CDK_DEPLOY_ACCOUNT and CDK_DEPLOY_REGION is not found in personal.env.yml.")
        #### Set API_DOMAIN, API_STAGE, API_PATH as env variable
       
        if app_api_domain :
            app_api_domain = app_api_domain
        elif 'app_api_domain' in personal_env_settings['environment']['personal'].keys() :
            app_api_domain =  personal_env_settings['environment']['personal']['app_api_domain']
        else :
            app_api_domain = ""
        api_domain = api_domain if api_domain else personal_env_settings['environment']['personal']['api_domain']
        api_stage =  api_stage if api_stage else personal_env_settings['environment']['personal']['api_stage']
        api_path = api_domain+"/"+api_stage
        logger.info("Setting up Env variables : APP_API_DOMAIN {}, API_DOMAIN {}, API_STAGE {}, API_PATH {}".format(app_api_domain, api_domain, api_stage, api_path))
        os.environ["APP_API_DOMAIN"] = app_api_domain
        os.environ["API_DOMAIN"] = api_domain
        os.environ["API_STAGE"] = api_stage
        os.environ["API_PATH"] = api_path
    elif env == 'dts':
        dts_env_settings = None
        try:
            with open("./env.yml", 'r') as stream:
                dts_env_settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
                logger.info(exc)
        except IOError:
                logger.info("env.yml not found!")
                sys.exit(1)
        aws_profile = profile if profile else dts_env_settings['environment'][env][stage].get('profile')
        domain = dts_env_settings['environment'][env][stage]['domain']
        log_info(logger, aws_profile, domain, env)
        #### Set APP_API_DOMAIN, API_DOMAIN, API_STAGE, API_PATH as env variable
        if app_api_domain :
            app_api_domain = app_api_domain
        elif 'app_api_domain' in dts_env_settings['environment'][env][stage].keys() :
            app_api_domain =  dts_env_settings['environment'][env][stage]['app_api_domain']
        elif 'app_api_domain' in dts_env_settings['environment'][env]["default"].keys() :
            app_api_domain =  dts_env_settings['environment'][env]["default"]['app_api_domain']
        else :
            app_api_domain = ""

        if api_domain :
            api_domain = api_domain
        elif 'api_domain' in dts_env_settings['environment'][env][stage].keys() :
            api_domain =  dts_env_settings['environment'][env][stage]['api_domain']
        elif 'api_domain' in dts_env_settings['environment'][env]["default"].keys() :
            api_domain =  dts_env_settings['environment'][env]["default"]['api_domain']
        else :
            api_domain = api_domain

        if api_stage :
            api_stage = api_stage
        elif 'api_stage' in dts_env_settings['environment'][env][stage].keys() :
            api_stage =  dts_env_settings['environment'][env][stage]['api_stage']
        elif 'api_stage' in dts_env_settings['environment'][env]["default"].keys() :
            api_stage =  dts_env_settings['environment'][env]["default"]['api_stage']
        else :
            api_stage = api_stage

        api_path = api_domain+"/"+api_stage
        logger.info("Setting up Env variables : APP_API_DOMAIN {}, API_DOMAIN {}, API_STAGE {}, API_PATH {}".format(app_api_domain, api_domain, api_stage, api_path))
        os.environ["APP_API_DOMAIN"] = app_api_domain
        os.environ["API_DOMAIN"] = api_domain
        os.environ["API_STAGE"] = api_stage
        os.environ["API_PATH"] = api_path
    else:
        prod_env_settings = None
        try:
            with open("./env.yml", 'r') as stream:
                prod_env_settings = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            logger.info(exc)
        except IOError:
            logger.info("env.yml not found!")
            sys.exit(1)
        aws_profile = profile if profile else prod_env_settings['environment'][env].get('profile')
        domain = prod_env_settings['environment'][env]['domain']
        log_info(logger, aws_profile, domain, env)
        #### Set APP_API_DOMAIN, API_DOMAIN, API_STAGE, API_PATH as env variable
        
        if app_api_domain :
            app_api_domain = app_api_domain
        elif 'app_api_domain' in prod_env_settings['environment'][env].keys() :
            app_api_domain =  prod_env_settings['environment'][env]['app_api_domain']
        else :
            app_api_domain = ""
            
        api_domain = api_domain if api_domain else prod_env_settings['environment'][env]['api_domain']
        api_stage = ""
        api_path = api_domain
        logger.info("Setting up Env variables : APP_API_DOMAIN {}, API_DOMAIN {}, API_STAGE {}, API_PATH {}".format(app_api_domain, api_domain, api_stage, api_path))
        os.environ["APP_API_DOMAIN"] = app_api_domain
        os.environ["API_DOMAIN"] = api_domain
        os.environ["API_STAGE"] = api_stage
        os.environ["API_PATH"] = api_path
    
    ### Setting Envrionment Variables
    logger.info("Setting up environment variables : AWS_APP_DOMAIN {}, AWS_PROFILE {}".format(domain, aws_profile))
    os.environ["AWS_APP_DOMAIN"] = domain
    if aws_profile :
       os.environ["AWS_PROFILE"] = aws_profile
    os.environ["STAGE"] = stage

    logger.info("Setting up environment variables : version {}".format(version))
    os.environ["version"] = version

    if command.lower() == 'bootstrap':
        shell(logger, "cdk bootstrap", raise_error=True)
    elif command.lower() == 'build':
        logger.debug("------------ Running Build --------------------")
        shell(logger, "npm run clean && npm run build",raise_error=True)
    elif command.lower() == 'deploy':
        # DTS GREEN: xxx-green-dev.dts-bobswift.appfire.app
        # DTS BLUE: xxx-dev.dts-bobswift.appfire.app
        # STANDALONE: xxx-dev.bobswift.lavadukanam.com
        # PROD: markdown.bobswift.appfire.app

        # default container registry for service modules
        registry_url = "951171940383.dkr.ecr.us-east-1.amazonaws.com"

        #app_domain = domain.split(".")[2] + "." + domain.split(".")[3] if env == 'standalone' else "appfire.app"
        app_domain = ".".join(domain.split(".")[2:]) if env == 'standalone' else "appfire.app"
        app_name = domain.split(".")[0].split("-")[0]
        #brand = domain.split(".")[1] if env != 'standalone' else "bobswift"
        brand = domain.split(".")[1].replace('dts-','') if env == 'dts' else domain.split(".")[1]
        logger.info("brand : "+ brand)
        #print(brand)
        #print(domain.split("."))
        app_suffix = 'green' if app_suffix == 'green' else ''
        
        
        #generate_base_url(logger, "web/static/atlassian-connect.json", app_suffix, domain, env)
        #generate_base_url(logger, "atlassian-connect.json", app_suffix, domain, env)

        logger.debug("overriding cdk.json with supplied arguments")
        logger.info("AWS home=" + aws_home)
        generate_cdk_json(logger, app_suffix, app_domain, env, stack, stage, brand, app_name)
        if stack == 'core':
            deploy_core(logger,app_name,api_stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag)
        elif stack == 'biz-service':
            deploy_biz_services(logger,app_name,stage,app_domain,brand,env,app_suffix,aws_profile)
        elif stack == 'app-service':
            deploy_app_services(logger,app_domain,brand,env,aws_profile)
        elif stack == 'module-service':
            deploy_module_services(logger,app_name,api_stage,app_domain,brand,env,app_suffix,aws_profile)
        elif stack == 'ac-allowlist':
            deploy_service_module(logger,stack,True,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-automation':
            deploy_service_module(logger,stack,True,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-core':
            deploy_service_module(logger,stack,False,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-data-engine-api':
            deploy_service_module(logger,"ac-data-engine-api",False,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-datastore':
            deploy_service_module(logger,"ac-datastore",False,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-macro-security':
            deploy_service_module(logger,stack,True,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-migrations':
            deploy_service_module(logger,stack,True,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-proxy':
            deploy_service_module(logger,stack,True,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        elif stack == 'ac-utils':
            deploy_service_module(logger,stack,True,app_name,api_stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag)
        else:
            if not aws_profile: checkCDKEnvVariables()
            ## Run build by default. Escape if false
            if build == True :
                logger.debug("------------ Running Build --------------------")
                shell(logger, "npm run clean && npm run build",raise_error=True)
            shell(logger,  "cdk deploy '*' {require_approval_arg} {profile_arg}".format(
                require_approval_arg="--require-approval "+require_approval,
                profile_arg=" --profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)
    elif command == 'diff':
        if not aws_profile: checkCDKEnvVariables()
        shell(logger, "cdk diff {profile_arg}".format(
            profile_arg=" --profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)
    elif command == 'synth':
        if not aws_profile: checkCDKEnvVariables()
        shell(logger, "cdk synth {profile_arg}".format(
            profile_arg=" --profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)
    elif command == 'destroy':
        if not aws_profile: checkCDKEnvVariables()
        shell(logger, "cdk destroy {stack_arg} {profile_arg}".format(
            stack_arg=stack,
            profile_arg=" --profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)
    elif command =="run":
        logger.debug("------------ Starting Ngrok on port 9000 --------------------")
        if token :
            # Set the user auth token for Ngrok
            conf.get_default().auth_token = token
        
        # Open a HTTP tunnel on port 9000
        http_tunnel = ngrok.connect(9000)
        
        # Set the AWS_APP_DOMAIN to the Ngrok public URL which is replaced in app's atlassian-connect.json
        os.environ["AWS_APP_DOMAIN"] = http_tunnel.public_url.replace('http://','')
        
        ## Always run the build since we start Ngrok here and need the url
        logger.debug("------------ Running Dev Build --------------------")
        shell(logger, "npm run clean && npm run build:dev",raise_error=True)

        shell(logger, "npm run start", raise_error=True)
    elif command =="build:dev":
        logger.debug("------------ Running Dev Build --------------------")
        shell(logger, "npm run clean && npm run build:dev",raise_error=True)
    else:
        if not aws_profile: checkCDKEnvVariables()
        shell(logger, "cdk list {profile_arg}".format(
            profile_arg=" --profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)

def deploy_core(logger,app_name,stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag):
    if deploy_biz_services(logger,app_name,stage,app_domain,brand,env,app_suffix,aws_profile) :
        if deploy_app_services(logger,app_domain,brand,env,aws_profile) :
            if deploy_service_module(logger,"ac-core",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                if deploy_service_module(logger,"ac-datastore",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                    if deploy_service_module(logger,"ac-allowlist",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                        if deploy_service_module(logger,"ac-automation",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                            if deploy_service_module(logger,"ac-macro-security",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                                if deploy_service_module(logger,"ac-migrations",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                                    if deploy_service_module(logger,"ac-proxy",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                                        if deploy_service_module(logger,"ac-utils",False,app_name,stage,app_domain,brand,env,app_suffix,aws_profile,registry_url,tag):
                                            if deploy_module_services(logger,app_name,stage,app_domain,brand,env,app_suffix,aws_profile):
                                                print('Core services deployed successfully.')

def deploy_biz_services(logger,app_name,stage,app_domain,brand,env,app_suffix,aws_profile):
    if not aws_profile: checkCDKEnvVariables()

    if (not os.path.isfile('./node_modules/ac-biz-services/bin/ac-biz-services.js')):
        logger.info('ac-biz-services dependency is not installed. Installing latest ac-biz-services.')
        shell(logger,"npm install ac-biz-services --save-dev",raise_error=True)

    shell(logger, "cdk deploy '*' --app \"npx ts-node ./node_modules/ac-biz-services/bin/ac-biz-services.js " + env + " " + stage + "\"" +  " {require_approval_arg} {profile_arg}".format(
                require_approval_arg=" --require-approval never",
                profile_arg=" --profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)
    return True

def deploy_app_services(logger,app_domain,brand,env,aws_profile):
    if not aws_profile: checkCDKEnvVariables()

    if (not os.path.isfile('./node_modules/ac-app-services/bin/ac-app-services.js')):
        logger.info('ac-app-services dependency is not installed. Installing latest ac-app-services.')
        shell(logger,"npm install ac-app-services --save-dev",raise_error=True)
    
    ## install dependencies for app services
    logger.info("Installing dependencies for App Services")

    shell(logger,"cd ./node_modules/ac-app-services/lib/lifecycle/construct/resources/lifecycle-node-layer/nodejs && npm install",raise_error=True)
    shell(logger,"cd ./node_modules/ac-app-services/lib/webhook-router/construct/resources && npm install",raise_error=True)
    shell(logger,"cd ./node_modules/ac-app-services/lib/waf-services/construct/resources/waf-shield && pip3 install requests -t ./",raise_error=True)

    shell(logger, "cdk deploy '*' --app \"npx ts-node ./node_modules/ac-app-services/bin/ac-app-services.js " + env
                                + " " + app_domain + " " + brand + "\"" + " {require_approval_arg} {profile_arg}".format(
                require_approval_arg="--require-approval never",
                profile_arg=" --profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)

    return True

def deploy_module_services(logger,app_name,stage,app_domain,brand,env,app_suffix,aws_profile):
    if (not os.path.isfile('./node_modules/ac-module-services/bin/ac-module-services.js')):
        logger.info('ac-module-services dependency is not installed. Installing latest ac-module-services.')
        shell(logger,"npm install ac-module-services --save-dev",raise_error=True)

    ## Deploying ac-module-services
    shell(logger, "cdk deploy '*' --app 'npx ts-node ./node_modules/ac-module-services/bin/ac-module-services.js " + env + " " + app_domain + " " + stage + "'" +  " {require_approval_arg} {profile_arg}".format(
                require_approval_arg="--require-approval never",
                profile_arg="--profile "+ aws_profile if aws_profile else ""
            ), raise_error=True)

    return True

def deploy_service_module(logger,service_module,module_services_deploy,app_name,stage,app_domain,brand,env,app_suffix,aws_home,aws_profile,registry_url,tag):
    logger.info('Deploying ' + service_module)

    if not aws_profile: checkCDKEnvVariables()

    # check to see if a tags yml file exist for the service modules
    service_module_tags = None
    try:
        with open('service-module-tags.yml', 'r') as stream:
            service_module_tags = yaml.safe_load(stream)
    except IOError:
        logger.info("service-module-tags.yml not found!")

    # check if a service module has a tag defined and use that instead of the default (latest)
    if service_module_tags is not None :
        if service_module in service_module_tags :
            if 'tag' in service_module_tags[service_module] :
                tag = service_module_tags[service_module]['tag']

    # Pull the service_module_image:tag
    service_module_image = generate_image_url(service_module,registry_url,tag)
    returnCode = shell(logger,"docker pull " + service_module_image,raise_error=False)

    if returnCode == 1:
        return False

    cdk_deploy = generate_cdk_deploy(aws_home, aws_profile, os.environ.get("CDK_DEPLOY_ACCOUNT"), os.environ.get("CDK_DEPLOY_REGION"))

    if service_module == "ac-automation":
        returnCode = shell(logger,cdk_deploy + " -e STAGE=" + stage  + " " + service_module_image,raise_error=False)
    elif service_module == "ac-core":
        returnCode = shell(logger,cdk_deploy + " -e ENV=" + env  + " -e DOMAIN=" + app_domain + " -e APP_SUFFIX=" + app_suffix + " " + service_module_image,raise_error=False)
    else: 
        returnCode = shell(logger,cdk_deploy + " -e ENV=" + env + " -e STAGE=" + stage + " " + service_module_image,raise_error=False)

    if returnCode == 1:
        return False

    if module_services_deploy == True:
        logger.info('Deploying ac-module-services')
        deploy_module_services(logger,app_name,stage,app_domain,brand,env,app_suffix,aws_profile)

    return True

def generate_cdk_json(logger, app_suffix, app_domain, env, stack, stage, brand, app_name):
    '''dynamically prepare cdk.json based on command line arguments'''
    
    try:
        with open('cdk.json', 'r') as file:
            json_data = json.load(file)
            for item in json_data:
                if item == 'app':
                    json_data[
                        item] = "npx ts-node ./node_modules/ac-app-dist/bin/ac-app-dist.js " + app_name + " " + stage \
                                + " " + app_domain + " client/dist " + brand + " " + env + " false " + app_suffix
        with open('cdk.json', 'w') as file:
            json.dump(json_data, file, indent=2)
    except IOError:
        shell(logger, "cdk.json not found!")


def generate_base_url(logger, path, app_suffix, domain, env):
    '''generate baseurl in atlassian-connect descriptor'''
    
    try:
        with open(path, 'r') as file:
            json_data = json.load(file)
            for item in json_data:
                if item == 'baseUrl':
                    if env == 'dts':
                        app_name = domain.split(".")[0].split("-")[0]
                        env_stage = domain.split(".")[0].split("-")[1]
                        domain = domain if app_suffix != 'green' else app_name + "-green-" + env_stage + "." + \
                                                                      domain.split(".")[1] + "." + \
                                                                      domain.split(".")[2] + "." + \
                                                                      domain.split(".")[3]
                    if env == 'prod':
                        app_name = domain.split(".")[0]
                        domain = domain if app_suffix != 'green' else app_name + "-green." + \
                                                                      domain.split(".")[1] + "." + \
                                                                      domain.split(".")[2] + "." + \
                                                                      domain.split(".")[3]
                    
                    json_data[item] = "https://" + domain
                if item == 'links':
                    json_data['links']['self'] = "https://" + domain + "/atlassian-connect.json"
        
        with open(path, 'w') as file:
            json.dump(json_data, file, indent=2)
    except IOError:
        shell(logger, path + " not found!")


def log_info(logger, aws_profile, domain, env):
    logger.info(f'Environment: {env}')
    logger.info(f'AWS Profile: {aws_profile}')
    logger.info(f'Domain: {domain}')

def shell(logger, cmd, raise_error=False):
    """
    Run a shell command.
    :param logger:
    :param cmd:  Shell line to be executed
    :param raise_error:
    :return: Tuple (return code, interleaved stdout and stderr output as string)
    """
    if (logger != None ):
      logger.info("Running : %s" % cmd)

    process = subprocess.run(
        cmd,
        check=False,
        shell=True
    )

    if raise_error and process.returncode != 0:
        raise ShellCommandFailed("The following command did not succeed: %s" % cmd)
    elif process.returncode != 0:
        sys.exit(process.returncode)

    return (process.returncode)

def dts_ecr_login(logger, profile):
    print(f"AWS DTS ECR Profile: {profile}")
    shell(None,"aws ecr get-login-password --region us-east-1 --profile " + profile +
                 " | docker login --username AWS --password-stdin 951171940383.dkr.ecr.us-east-1.amazonaws.com")

def generate_image_url(service_module,registry_url,tag):
    return registry_url + "/" + service_module + ":" + tag

def generate_cdk_deploy(aws_home,aws_profile,cdk_deploy_account,cdk_deploy_region):

    # Build a CDK deploy string based either on AWS_PROFILE or AWS ENV Args
    if aws_profile:
        cdk_deploy = "docker run {aws_home_arg} {cdk_deploy_account_arg} {cdk_deploy_region_arg} {profile_arg}".format(
            aws_home_arg=" -v " + aws_home + ":/appfire/.aws",
            cdk_deploy_account_arg="-e CDK_DEPLOY_ACCOUNT="+cdk_deploy_account,
            cdk_deploy_region_arg="-e CDK_DEPLOY_REGION="+ cdk_deploy_region,
            profile_arg="-e AWS_PROFILE="+ aws_profile)
    else:
        checkCDKEnvVariables()

        cdk_deploy = "docker run {cdk_deploy_account_arg} {cdk_deploy_region_arg} {aws_default_region_arg} {aws_access_key_id_arg} {aws_secret_access_key_arg}".format(
            aws_access_key_id_arg="-e AWS_ACCESS_KEY_ID="+ os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key_arg="-e AWS_SECRET_ACCESS_KEY="+ os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_default_region_arg="-e AWS_DEFAULT_REGION="+ cdk_deploy_region,
            cdk_deploy_account_arg="-e CDK_DEPLOY_ACCOUNT="+cdk_deploy_account,
            cdk_deploy_region_arg="-e CDK_DEPLOY_REGION="+ cdk_deploy_region)

    print(f"Generated CDK={cdk_deploy}")
    return cdk_deploy

def list_tags(logger, profile, stack):
    shell(logger,"aws ecr describe-images --output yaml --repository-name " + stack + " --profile " + profile
    + " --no-cli-pager --query \'sort_by(imageDetails[?imageTags!=null],& imagePushedAt)[*].{Tag: imageTags}\'")

def list_stacks(logger):
    print("Data Engine: ac-data-engine-api")
    print("Datastore: ac-datastore")
    print("Other: [ac-biz-service, ac-app-service, core, module-service]")
    print("Service Module Stacks: [", *service_modules, "]")

def run_pipeline(logger,stack, bitbucket_username,bitbucket_password,bitbucket_branch,bitbucket_tag_value):
    headers = {
        'Content-Type': 'application/json',
    }

    data = '{ "target": { "type": "pipeline_ref_target", "ref_type": "branch", "ref_name": "' + bitbucket_branch + '", "selector": { "type": "custom", "pattern": "build-push-image" } }, "variables": [ { "key": "TAG", "value": "' + bitbucket_tag_value + '"} ] }'
    logger.info(data)
    pipeline_url = f"https://api.bitbucket.org/2.0/repositories/appfire/{stack}/pipelines/"
    response = requests.post(pipeline_url, headers=headers, data=data, auth=(bitbucket_username, bitbucket_password))
    if (response.status_code == 201):
        logger.info("Pipeline started...")
    else:
        logger.info(f"Pipeline failed to start - {response.status_code}")
    return response

def docker_build(logger,tag, disable_clone_prompt):
    repo_name = git("config", "--get", "remote.origin.url")

    service_module = isValidServiceModuleGitRepo(repo_name.stdout.decode())
    if service_module == "":
        print(f"Not a service module git repository directory, valid service modules [",  *service_modules, "]")
        sys.exit(1)

    docker_build = f"docker build -f ac-tools/dockerfiles/service-module/Dockerfile -t 951171940383.dkr.ecr.us-east-1.amazonaws.com/{service_module}:custom-{tag} --build-arg REPO_NAME={service_module} ."
    docker_push = f"docker push 951171940383.dkr.ecr.us-east-1.amazonaws.com/{service_module}:custom-{tag}"

    try:
        cloneBy = questionary.select(
        "The Dockerfile for the build will be cloned from bitbucket.org/appfire/ac-tools. How to clone it?",
        choices=[
            'ssh',
            'https'
         ]).skip_if(disable_clone_prompt, default=True).ask()  # returns value of selection
        checkForKeyboardInterrupt(cloneBy)
    except KeyboardInterrupt:
        sys.exit(1)

    gitLink = "git@bitbucket.org:appfire/ac-tools.git"
    if cloneBy == 'https':
        userName = questionary.text(
            "Enter your git user name:"
        ).ask()  # returns the name of the user in Bitbucket
        checkForKeyboardInterrupt(userName)
        gitLink = "https://{}@bitbucket.org/appfire/ac-tools.git".format(userName)

    if (os.path.isdir("ac-tools")): shutil.rmtree("ac-tools")

    ret = git("clone", gitLink, "--single-branch")

    if ret.returncode != 0:
        print(ret.stderr)
        sys.exit(1)

    shutil.rmtree("cdk.out", True)

    shell(None, docker_build)
    shell(None, docker_push)

    print("Run" +  '\033[32m' + f" appfire deploy --stack {service_module} --tag custom-{tag} [options]")
    shutil.rmtree("ac-tools")

def git(*args):
    return subprocess.run(['git'] + list(args), stdout=PIPE, stderr=PIPE)

def checkForKeyboardInterrupt(value):
    if value is None:
        raise KeyboardInterrupt

def isValidServiceModuleGitRepo(repoPath):
    if repoPath == "":
        return ""

    for service_module in service_modules:
        if service_module != "":
            len  = repoPath.find(service_module)
            if len > 0:
                return service_module

    return ""

def checkCDKEnvVariables():

    if os.getenv("AWS_ACCESS_KEY_ID") is None or os.getenv("AWS_SECRET_ACCESS_KEY") is None:
        print(f"AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set.")
        sys.exit(1)
class ShellCommandFailed(Exception):
    """ Executing a shell command failed """

if __name__ == "__main__":
    process()
