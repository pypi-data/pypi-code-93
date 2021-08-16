# -*- coding: utf-8 -*-

CLI_VERSION = "2020-08-10"

ASSUME_ROLE_ARN = 'YXJuOmF3cy1jbjppYW06OjQ0NDYwMzgwMzkwNDpyb2xlL1BoLUNsaS1MbWQ='
ASSUME_ROLE_EXTERNAL_ID = 'Ph-Cli-Lmd'

DEFAULT_BUCKET = "ph-platform"
DEFAULT_TEMPLATE_DIR = "/template/python/phcli/lmd/"
DEFAULT_LAYER_DIR = "/layers/#runtime#/#name#/"
DEFAULT_LAMBDA_DIR = "/functions/#runtime#/#name#/"

LAMBDA_LAYER_MAX_VERSION_NUM = 5
LAMBDA_FUNCTION_MAX_VERSION_NUM = 5
LAMBDA_FUNCTION_ALIAS_NAME_CUR = 'current'
LAMBDA_FUNCTION_ALIAS_NAME_PREV = 'previous'

DEPLOY_FILE_TEMPLATE_NAME = 'ph-lambda-deploy-template.yaml'
DEPLOY_FILE_LOCAL_NAME = '.ph-lambda-deploy.yaml'
