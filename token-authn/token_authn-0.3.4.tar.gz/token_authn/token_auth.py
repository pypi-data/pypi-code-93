from fastapi import Request, HTTPException, Response, status
import jose.jwt as jwt
import os
import traceback as tb
import json
import datetime
import time

import boto3
import base64
from botocore.exceptions import ClientError

from boto3 import resource
from fastapi import Depends, Response, status



def get_secret(secret_name):

    # secret_name = "dev-ml"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret


def verify_token(req: Request, response: Response):
    if 'authorization' in req.headers.keys():
        token = req.headers["authorization"].split(' ')[1]
    else:
        return False
    #TODO add expiration time as part of a json
    exp_time = 24*60*60

    # Get the JWT token secret
    try:
        env = os.environ.get('ECS_CLUSTER_NAME')
        secrets = get_secret(env)#os.environ.get('ECS_CLUSTER_NAME'))
        secrets = json.loads(secrets)
        jwt_secret_token = secrets['JWT_TOKEN_SECRET']
    except Exception as e:
        print(str(e))
        print(tb.format_exc())
        secrets = []
        return False

    try:
        payload = jwt.decode(
            token,
            key=jwt_secret_token
        )
        expiration = payload['exp'] if 'exp' in payload.keys() else 0
        if expiration == 0:
            if payload['iat']+exp_time>time.mktime(datetime.date.today().timetuple()):
                return True
            else:
                return False
            
        else:
            if datetime(expiration)>datetime.now():
                return True
            else:
                return False
        return True
    except Exception as e:
        print(str(e))
        print(tb.format_exc())
        return False


def verify(response: Response, authorized: bool = Depends(verify_token)):
    if not authorized:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {'error': 'Unauthorized'}