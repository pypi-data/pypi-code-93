# pylint: disable=super-with-arguments
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

"""
    GLUE TASK CODE
        - these are used in pythonOperator steps as a way \
            to flexibly call boto3 and perform any special requirements
"""
import json
import logging
from datetime import datetime, timedelta

import boto3
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)


class StartQuery(BaseOperator):
    """
    Queries CloudWatch Logs. CloudWatch Logs Insights supports a query language
    you can use to perform queries on your log groups. Each query can include one
    or more query commands.
    Query Syntax: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html

    Queries time out after 15 minutes of execution.
    If your queries are timing out, reduce the time range being searched
    or partition your query into a number of queries.
    """
    template_fields = ('config', 'xcom_tasks',)

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(StartQuery, self).__init__(*args, **kwargs)

        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            :config.job_name: str. the name of the glue job to run.
            :config.job_arguments: dict. the key value arguments send to the job.
            :xcom_push: str. glue_job_run_id.
        """
        LOGS_CLIENT = boto3.client('logs')

        query = self.config.get('query', 'fields @timestamp, @message | sort @timestamp desc')
        log_groups = self.config.get('log_groups', None)
        hour_delta = self.config.get('hour_delta', 5)
        limit = self.config.get('query', 100)

        try:
            # Start query and gather query id
            query_id = LOGS_CLIENT.start_query(
                logGroupNames=log_groups,
                # filter by current time to specified time delta
                startTime=int((datetime.today() - timedelta(hours=hour_delta)).timestamp()),
                endTime=int(datetime.now().timestamp()),
                queryString=query,
                limit=limit
            )['queryId']

            context['task_instance'].xcom_push(
                key='query_id',
                value=query_id
            )

        except Exception as err:
            raise err


class LogToS3(BaseOperator):
    """
    Returns the results from the specified query made from a log group
    using CloudWatch Logs Insights. The data returned is saved as
    json in S3 in the specified bucket and key.
    """
    template_fields = ('config', 'xcom_tasks',)

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(LogToS3, self).__init__(*args, **kwargs)

        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """
            :config.job_name: str. the name of the glue job to run.
            :config.job_arguments: dict. the key value arguments send to the job.
            :xcom_push: str. glue_job_run_id.
        """
        LOGS_CLIENT = boto3.client('logs')
        S3_CLIENT = boto3.client('s3')

        s3_bucket = self.config.get('s3_bucket', None)
        s3_key = self.config.get('s3_key', None)

        if s3_bucket is None or s3_key is None:
            raise ValueError('S3 location is not specified')

        query_id = self.config.get('query_id', None)
        task_ids = self.xcom_tasks['query_id']['task_id']

        if query_id is None:
            query_id = context['task_instance'].xcom_pull(
                task_ids=task_ids,
                key=self.xcom_tasks['query_id']['key']
            )

        try:
            cloud_watch_logs = LOGS_CLIENT.get_query_results(
                queryId=query_id
            )

            S3_CLIENT.put_object(
                Body=json.dumps(cloud_watch_logs),
                Bucket=s3_bucket,
                Key=f'{s3_key}/{datetime.now()}.json'
            )
        except Exception as err:
            raise err
