import boto3
import sagemaker
from sagemaker import get_execution_role
import json
import tarfile
import os
from time import gmtime, strftime

def deploy_multi_model_endpoint(endpoint_name, 
                   model_url, 
                   container, 
                   role=None, 
                   sm_client=None, 
                   runtime_sm_client=None, 
                   model_name=None, 
                   endpoint_config_name=None,
                   use_timestamp=False
                  ):
    # 加个后缀
    if use_timestamp:
        endpoint_name = str(endpoint_name) + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    
    # model_url 必须以'/'结尾
    if not model_url.endswith('/'):
        raise ValueError('Parameter model_url is a folder and must ends with "/"!')
    
    if type(role) == type(None):
        role = get_execution_role()
    
    if type(sm_client) == type(None):
        sm_client = boto3.client(service_name='sagemaker')
    
    if type(runtime_sm_client) == type(None):
        runtime_sm_client = boto3.client(service_name='sagemaker-runtime')
    
    if type(model_name) == type(None):
        model_name = endpoint_name
    
    if type(endpoint_config_name) == type(None):
        endpoint_config_name = endpoint_name
    
    container = {
        'Image': container,
        'ModelDataUrl': model_url,
        'Mode': 'MultiModel',
    }
    
    ###
    # create model
    create_model_response = sm_client.create_model(
        ModelName = model_name,
        ExecutionRoleArn = role,
        Containers = [container])
    print('Model name: ' + model_name)
    ###
    # create endpoint config
    endpoint_config_name = model_name
    
    create_endpoint_config_response = sm_client.create_endpoint_config(
        EndpointConfigName = endpoint_config_name,
        ProductionVariants=[{
            'InstanceType': 'ml.m5.large',
            'InitialInstanceCount': 2,
            'InitialVariantWeight': 1,
            'ModelName': model_name,
            'VariantName': 'AllTraffic'}])
    print('Endpoint config name: ' + endpoint_config_name)
    
    ###
    # create endpoint
    create_endpoint_response = sm_client.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=endpoint_config_name)
    
    print('Endpoint name: ' + endpoint_name)
    print('Endpoint Arn: ' + create_endpoint_response['EndpointArn'])
    
    resp = sm_client.describe_endpoint(EndpointName=endpoint_name)
    status = resp['EndpointStatus']
    print("Endpoint Status: " + status)
    
    # Wating for endpoint in service
    print('Waiting for {} endpoint to be in service...'.format(endpoint_name))
    waiter = sm_client.get_waiter('endpoint_in_service')
    waiter.wait(EndpointName=endpoint_name)
'''
# endpoint的名字
endpoint_name = 'demo-ml'
# 模型列表，注意最后结尾带上 /
model_url = 's3://sagemaker-ca-central-1-337058716437/test-mlops-2021-08-16-10-29-58-163/output/'
# container的地址
container = '337058716437.dkr.ecr.ca-central-1.amazonaws.com/xgboost-multi'

deploy_my_code(endpoint_name,  model_url, container, use_timestamp=True)
'''