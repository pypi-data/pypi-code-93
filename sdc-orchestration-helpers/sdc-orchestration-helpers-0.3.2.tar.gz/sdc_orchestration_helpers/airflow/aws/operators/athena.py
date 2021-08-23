# pylint: disable=super-with-arguments
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

"""
    ATHENA TASK CODE
        - these are used in pythonOperator steps as a way \
            to flexibly call boto3 and perform any special requirements
"""
import os
import logging
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import boto3
from botocore.exceptions import ClientError as botocore_clienterror

logger = logging.getLogger(None)

class StartQueryExecution(BaseOperator):
    template_fields = ('config',)

    @apply_defaults
    def __init__(self, config, *args, **kwargs):
        super(StartQueryExecution, self).__init__(*args, **kwargs)
        self.config = config

    def execute(self, context):
        """
            Runs athena query against feature store

            https://sagemaker.readthedocs.io/en/stable/api/\
                prep_data/feature_store.html#sagemaker.feature_store.feature_group.AthenaQuery
        """
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        ATHENA_CLIENT = BOTO_SESSION.client('athena')

        try:
            response = ATHENA_CLIENT.start_query_execution(
                QueryString=self.config['query'],
                QueryExecutionContext=self.config.get('query_execution_context', {}),
                ResultConfiguration=self.config['result_configuration'],    
                WorkGroup=self.config['workgroup']
            )

            context['task_instance'].xcom_push(
                key='athena_query_execution_id',
                value=response['QueryExecutionId']
            )

        except Exception as err:
            raise
