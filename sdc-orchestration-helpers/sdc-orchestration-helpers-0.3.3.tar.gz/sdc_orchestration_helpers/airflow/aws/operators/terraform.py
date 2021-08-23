# pylint: disable=super-with-arguments
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

"""
    TERRAFORM TASK CODE
        - these are used in pythonOperator steps as a way \
            to flexibly call boto3 and perform any special requirements
"""
import json
import logging

import boto3
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)


class GetRemoteTfstate(BaseOperator):
    """
       A process of collecting the relevant tfstate resources based on the terraform
       tags provided. If tags are not provided, the entire tfstate resources are returned.
    """
    template_fields = ('config', 'xcom_tasks',)

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(GetRemoteTfstate, self).__init__(*args, **kwargs)

        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """

        """
        s3 = boto3.client('s3')

        s3_bucket_name = self.config.get('s3_bucket_name', None)
        s3_bucket_key = self.config.get('s3_bucket_key', None)
        terraform_tags = self.config.get('terraform_tags', None)

        try:
            obj = s3.get_object(
                Bucket=s3_bucket_name, Key=s3_bucket_key
            )

            tfstate_raw_data = json.loads(obj['Body'].read())

            tfstate_resources = tfstate_raw_data.get('resources')
            tfstate_data = []
            for tfstate_instance in tfstate_resources:
                tags = tfstate_instance.get('instances')[0].get('attributes').get('tags', {})
                name = tfstate_instance \
                    .get('instances')[0] \
                    .get('attributes') \
                    .get('name',
                         # here if name does not exist, then the name is found in the id
                         tfstate_instance \
                         .get('instances')[0] \
                         .get('attributes') \
                         .get('id', None)
                         )
                type = tfstate_instance.get('type', None)

                if terraform_tags is not None:
                    if tags.get('client') == terraform_tags.get('client') \
                            and tags.get('service') == terraform_tags.get('service') \
                            and tags.get('environment') == terraform_tags.get('environment'):

                        if terraform_tags.get('use_case') in name:
                            tfstate_data.append({
                                'resource_name': name,
                                'resource_tags': tags,
                                'resource_type': type
                            })

            context['task_instance'].xcom_push(
                key='remote_tfstate',
                value=tfstate_data
            )

        except Exception as err:
            raise err
