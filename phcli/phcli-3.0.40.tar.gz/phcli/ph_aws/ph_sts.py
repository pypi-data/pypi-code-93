# -*- coding: utf-8 -*-
import boto3
import botocore.exceptions
from phcli.ph_aws.aws_root import PhAWS


class PhSts(PhAWS):
    def __init__(self, **kwargs):
        self.credentials = None
        self.access_key = kwargs.get('access_key', None)
        self.secret_key = kwargs.get('secret_key', None)

    def get_cred(self):
        if self.credentials:
            return {
                'region_name': 'cn-northwest-1',
                'aws_access_key_id': self.credentials['AccessKeyId'],
                'aws_secret_access_key': self.credentials['SecretAccessKey'],
                'aws_session_token': self.credentials['SessionToken'],
            }

    def assume_role(self, role_arn, external_id):
        if self.access_key and self.secret_key:
            sts_client = boto3.client('sts', region_name='cn-northwest-1',
                                      aws_access_key_id=self.access_key,
                                      aws_secret_access_key=self.secret_key)
        else:
            sts_client = boto3.client('sts', region_name='cn-northwest-1')

        try:
            assumed_role_object = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=external_id,
                ExternalId=external_id,
            )
        except botocore.exceptions.ClientError:
            self.credentials = {}
        else:
            self.credentials = assumed_role_object['Credentials']

        return self
