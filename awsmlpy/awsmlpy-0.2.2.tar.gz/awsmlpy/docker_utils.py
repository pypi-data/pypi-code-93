import boto3
import base64
import docker

def build_docker(tag, path='.'):
    print('*' * 30)
    print('Start building')
    docker_client = docker.from_env()
    image, build_log = docker_client.images.build(
        path=path, tag=tag, rm=True)
    for line in build_log:
        if 'stream' in line:
            print(line['stream'],end='')
    return image

def push_to_ecr(image, ecr_repo_name):
    print('*' * 30)
    print('Start pushing')
    sess = boto3.Session()
    resp = sess.client('ecr').get_authorization_token()
    token = resp['authorizationData'][0]['authorizationToken']
    token = base64.b64decode(token).decode()
    username, password = token.split(':')
    auth_config = {'username': username, 'password': password}
    
    ecr_url = resp['authorizationData'][0]['proxyEndpoint']
    
    client = docker.from_env()
    
    try:
        ecr_client = boto3.client('ecr')
        response = ecr_client.create_repository(
            repositoryName=ecr_repo_name,
        )
        print('[Info]Repository {} created'.format(ecr_repo_name))
    except:
        print('[Info]Repository {} existed'.format(ecr_repo_name))
    
    ecr_repo_name = '{}/{}'.format(
        ecr_url.replace('https://', ''), ecr_repo_name)
    print(ecr_repo_name)
    
    image.tag(ecr_repo_name, tag='latest')
    
    push_log = client.images.push(ecr_repo_name, auth_config=auth_config)
    print(push_log.replace('"status":"', '').replace('{', '').replace('}', '').replace(']', '').replace('"', ''))
    return ecr_repo_name

def build_and_push(tag, dockerfile_path, ecr_repo_name):
    image = build_docker(tag, dockerfile_path)
    print('\n\n\n')
    ecr_repo_name = push_to_ecr(image, ecr_repo_name)
    return ecr_repo_name

# from docker_utils import build_and_push

# image = build_and_push(tag='xgboost_001', dockerfile_path='/home/ec2-user/SageMaker/self_docker', ecr_repo_name='xgboost_001')