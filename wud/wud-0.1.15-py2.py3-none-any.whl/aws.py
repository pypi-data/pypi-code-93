 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 08:31:01 2021

@author: nattawoot
"""
import os
import json
from datetime import datetime, date, time
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, ParamValidationError
from loguru import logger

from wud.helper import logger_wraps, timeit, EnhancedJSONEncoder,EnhancedJSONDecoder


#%% AWS S3
            
def get_aws_keys():
    
    # AWS Lambda reserve AWS_ACCESS_KEY_ID, AWS_ACCESS_SECRET_KEY for thier temporary key
    if(os.environ.get('AWS_SESSION_TOKEN')):
        ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID_2')
        ACCESS_SECRET_KEY = os.environ.get('AWS_ACCESS_SECRET_KEY_2')    
    
    else:
        # s3
        ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
        ACCESS_SECRET_KEY = os.environ.get('AWS_ACCESS_SECRET_KEY')
        
        #conda not imported above name
        if(ACCESS_SECRET_KEY==None):
            ACCESS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
            
    return ACCESS_KEY_ID, ACCESS_SECRET_KEY
            
def get_s3_object(client_resource, region='us-east-1'):
    
    ACCESS_KEY_ID, ACCESS_SECRET_KEY = get_aws_keys()

    
    if client_resource == 'client':
        s3 = boto3.client(
        "s3",
        region_name = region,
        aws_access_key_id = ACCESS_KEY_ID,
        aws_secret_access_key = ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
    else:
        s3 = boto3.resource(
        "s3",
        aws_access_key_id = ACCESS_KEY_ID,
        aws_secret_access_key = ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4')
    )
        
    return s3            

def s3bucket_img_put(bucket, img_data, name_and_location):
        
    s3 = get_s3_object('resource')

    response = s3.Bucket(bucket).put_object(
        Key=name_and_location, ContentType="image/jpeg", Body=img_data
    )
    logger.success(f"{response} save pic to S3 done")
    
def s3bucket_img_get(bucket, name_and_location):
    
    s3 = get_s3_object('resource')

    file_name = name_and_location.split('/')[-1]
    #output = f"downloads/{file_name}"

    #response = s3.Bucket(bucket).download_file(file_name, output)
    
    file = s3.Object(bucket, name_and_location)
    
    return file
    
    
    #logger.success(f"{response} get pic from S3 done")
    
@timeit
@logger_wraps(exit=False)
def s3bucket_json_get(bucket, file_names):

    s3 = get_s3_object('resource')
    
    if(type(file_names) is str):
        content_object = s3.Object(bucket, file_names)
        file_content = content_object.get()['Body'].read().decode('utf-8-sig')
        json_content = json.loads(file_content, cls=EnhancedJSONDecoder)
        
        result = json_content
        
    else:
        json_contents = []
        for file_name in file_names:
            content_object = s3.Object(bucket, file_name)
            file_content = content_object.get()['Body'].read().decode('utf-8-sig')
            json_content = json.loads(file_content, cls=EnhancedJSONDecoder)
            json_contents.append(json_content)
            
        logger.debug(f'get {len(file_names)} from bucket')
    
        result = json_contents
        
    return result 

def s3bucket_json_put(bucket, file_name, json_dict):
    
    s3 = get_s3_object('resource')

    content_object = s3.Object(bucket, file_name)
    object_data = json.dumps(json_dict, indent=4, cls=EnhancedJSONEncoder)
    content_object.put(Body=object_data)
    
    return 'update done'

def s3bucket_object_put(bucket, file_name, object_data):
    s3 = get_s3_object('resource')

    content_object = s3.Object(bucket, file_name)
    content_object.put(Body=object_data)
    
    return 'upload done'



def s3bucket_list_filter(bucket, filter_keyword):
    
    s3 = get_s3_object('resource')

    my_bucket = s3.Bucket(bucket)
    result = []
    for obj in my_bucket.objects.all():
        if filter_keyword in obj.key:
            result.append(obj.key)
    
    return result

def create_presigned_url(bucket_name, object_name, region='us-east-1', expiration=21600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3 = get_s3_object('client', region)

    
    try:
        response = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration

                                                    )
    except ClientError as e:
         logger.warning(e)
         return None

    # The response contains the presigned URL
    return response    

