"""Main module.

Functions grabbed from here: https://github.com/awslabs/aws-batch-helpers/blob/master/gpu-example/submit-job.py
"""

import copy
import typing
import boto3
import time
import sys
from typing import TYPE_CHECKING, List, Dict, Any
from datetime import datetime
from botocore.compat import total_seconds
from pprint import pprint
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_batch.client import BatchClient
from mypy_boto3_batch.type_defs import DescribeJobDefinitionsResponseTypeDef
from mypy_boto3_batch.type_defs import JobDefinitionTypeDef
from mypy_boto3_batch.type_defs import RegisterJobDefinitionRequestRequestTypeDef
from mypy_boto3_batch.type_defs import RegisterJobDefinitionResponseTypeDef
from mypy_boto3_batch.type_defs import DescribeJobsResponseTypeDef
from mypy_boto3_batch.type_defs import SubmitJobRequestRequestTypeDef
from mypy_boto3_batch.type_defs import SubmitJobResponseTypeDef
from mypy_boto3_batch.literals import JobStatusType

from mypy_boto3_logs.client import CloudWatchLogsClient
from mypy_boto3_logs.type_defs import GetLogEventsResponseTypeDef
from mypy_boto3_logs.type_defs import OutputLogEventTypeDef
import logging

submit_logger = logging.getLogger('submit_logger')
watch_logger = logging.getLogger('watch_logger')
cloudwatch_logger = logging.getLogger('cloudwatch_logger')


def get_human_readable_time(last_time_stamp):
    return datetime.fromtimestamp(
        last_time_stamp / 1000.0).isoformat()


def find_or_create_job_definition(client: BatchClient, job_definition_name: str, job_definition: RegisterJobDefinitionRequestRequestTypeDef) -> List[JobDefinitionTypeDef]:
    assert job_definition_name, 'job_definition_name required'

    job_definitions_response: DescribeJobDefinitionsResponseTypeDef = client.describe_job_definitions(
        jobDefinitionName=job_definition_name)
    # job_definitions_response
    job_definitions: List[JobDefinitionTypeDef] = job_definitions_response.get(
        'jobDefinitions')

    if job_definitions[0]:
        job_definition_copy = copy.deepcopy(job_definitions[0])
        del job_definition_copy['jobDefinitionArn']
        del job_definition_copy['revision']
        del job_definition_copy['status']
        if not job_definition_copy == job_definition:
            register_job_definition_response: RegisterJobDefinitionResponseTypeDef = client.register_job_definition(
                **job_definition)
        else:
            return job_definitions[0]
    else:
        register_job_definition_response: RegisterJobDefinitionResponseTypeDef = client.register_job_definition(
            **job_definition)

    job_definitions_response: DescribeJobDefinitionsResponseTypeDef = client.describe_job_definitions(
        jobDefinitionName=register_job_definition_response['jobDefinitionName']
    )
    job_definition = job_definitions_response['jobDefinitions'][0]

    return job_definition


def get_log_stream_name(job_response: DescribeJobsResponseTypeDef) -> str:
    try:
        log_stream_name = job_response['jobs'][0]['container']['logStreamName']
    except Exception as e:
        log_stream_name = None
        cloudwatch_logger.exception("Exception occurred")
        cloudwatch_logger.error(job_response['jobs'])

    return log_stream_name


def get_log_events(client: CloudWatchLogsClient, log_group, log_stream_name, start_time=0, skip=0, start_from_head=True):
    """
    A generator for log items in a single stream. This will yield all the
    items that are available at the current moment.

    Completely stole this from here 
    https://airflow.apache.org/docs/apache-airflow/1.10.5/_modules/airflow/contrib/hooks/aws_logs_hook.html

    :param log_group: The name of the log group.
    :type log_group: str
    :param log_stream_name: The name of the specific stream.
    :type log_stream_name: str
    :param start_time: The time stamp value to start reading the logs from (default: 0).
    :type start_time: int
    :param skip: The number of log entries to skip at the start (default: 0).
        This is for when there are multiple entries at the same timestamp.
    :type skip: int
    :param start_from_head: whether to start from the beginning (True) of the log or
        at the end of the log (False).
    :type start_from_head: bool
    :rtype: dict
    :return: | A CloudWatch log event with the following key-value pairs:
             |   'timestamp' (int): The time in milliseconds of the event.
             |   'message' (str): The log event data.
             |   'ingestionTime' (int): The time in milliseconds the event was ingested.
    """

    next_token = None

    event_count = 1
    while event_count > 0:
        if next_token is not None:
            token_arg = {'nextToken': next_token}
        else:
            token_arg = {}

        response: GetLogEventsResponseTypeDef = client.get_log_events(logGroupName=log_group,
                                                                      logStreamName=log_stream_name,
                                                                      startTime=start_time,
                                                                      startFromHead=start_from_head,
                                                                      **token_arg)

        events = response['events']
        event_count = len(events)

        if event_count > skip:
            events = events[skip:]
            skip = 0
        else:
            skip = skip - event_count
            events = []

        for ev in events:
            yield ev

        if 'nextForwardToken' in response:
            next_token = response['nextForwardToken']
        else:
            return


def print_logs(client: CloudWatchLogsClient, log_stream_name: str, start_time: int = 0):
    log_events: List[OutputLogEventTypeDef] = get_log_events(client, log_group='/aws/batch/job',
                                                             log_stream_name=log_stream_name, start_time=start_time)

    last_time_stamp =  start_time 
    for log_event in log_events:
        last_time_stamp = log_event['timestamp']
        human_timestamp  = get_human_readable_time(last_time_stamp)
        message = log_event['message']
        cloudwatch_logger.info(f'[{human_timestamp}] {message}')

    if last_time_stamp > 0:
        last_time_stamp = last_time_stamp + 1

    return last_time_stamp


def watch_job(batch_client: BatchClient, log_client: CloudWatchLogsClient, job_response: DescribeJobsResponseTypeDef) -> JobStatusType:
    """Watch an AWS Batch job and print out the logs

    Shoutout to aws labs:
    https://github.com/awslabs/aws-batch-helpers/blob/master/gpu-example/submit-job.py

    Args:
        batch_client (BatchClient): boto3.client('batch') 
        log_client (CloudWatchLogsClient): boto3.client('logs')
        job_response (DescribeJobsResponseTypeDef): batch_client.describe_jobs(jobs=[jobId])  

    Returns:
        JobStatusType: AWS Batch Job Status 
    """
    spinner = 0
    running = False
    start_time = 0
    wait = True
    spin = ['-', '/', '|', '\\', '-', '/', '|', '\\']
    job_id = job_response['jobs'][0]['jobId']
    job_name = job_response['jobs'][0]['jobName']
    log_stream_name: Any = None
    line = '=' * 80

    while wait:
        time.sleep(1)
        describe_jobs_response: DescribeJobsResponseTypeDef = batch_client.describe_jobs(jobs=[
                                                                                         job_id])
        status: JobStatusType = describe_jobs_response['jobs'][0]['status']

        if status == 'SUCCEEDED' or status == 'FAILED':
            log_stream_name = get_log_stream_name(
                job_response=describe_jobs_response)

            if not running and log_stream_name:
                running = False
                watch_logger.info(f'Job [{job_name} - {job_id}] is COMPLETE with status: {status}')
                # print('\rJob [%s - %s] is COMPLETE with status: %s.' %
                #       (job_name, job_id, status))
                # print('Output [%s]:\n %s' % (log_stream_name, '=' * 80))
                watch_logger.info(f'Logs for log stream: {log_stream_name}:')

            if log_stream_name:
                start_time = print_logs(client=log_client,
                                        log_stream_name=log_stream_name,
                                        start_time=start_time)

            watch_logger.info(f'{line}\nJob [{job_name} - {job_id}] {status}')

            break

        elif status == 'RUNNING':

            log_stream_name = get_log_stream_name(
                job_response=describe_jobs_response)

            if not running and log_stream_name:
                running = True
                watch_logger.info(f'Job [{job_name} - {job_id}] is RUNNING')
                watch_logger.info(f'Polling cloudwatch logs...')
                watch_logger.info(f'Output for logstream: {log_stream_name}:\n{line}')
            if log_stream_name:
                start_time = print_logs(client=log_client,
                                        log_stream_name=log_stream_name,
                                        start_time=start_time)

        else:
            this_spin = spin[spinner % len(spin)]
            watch_logger.info(f'Job [{job_name} - {job_id}] is: {status}... {this_spin}')
            sys.stdout.flush()
            time.sleep(30)
            spinner += 1

    return status


def submit_batch_job(batch_client: BatchClient, log_client: CloudWatchLogsClient, submit_job: SubmitJobRequestRequestTypeDef) -> DescribeJobsResponseTypeDef:
    """Submit job to AWS Batch and wait for it

    Args:
        batch_client (BatchClient): boto3.client('batch') 
        log_client (BatchClient): boto3.client('batch') 
        submit_job (SubmitJobRequestRequestTypeDef): Submit object to AWS Batch 
    """
    try:
        response: SubmitJobResponseTypeDef = batch_client.submit_job(**submit_job)
    except Exception as e:
        submit_logger.exception("Exception occured submitting job")

    jobId = response['jobId']
    job_response: DescribeJobsResponseTypeDef = batch_client.describe_jobs(
        jobs=[
            jobId
        ]
    )
    return jobId, job_response
    # status = watch_job(batch_client=batch_client,
    #                    log_client=log_client, job_response=job_response)
    # job_response: DescribeJobsResponseTypeDef = batch_client.describe_jobs(
    #     jobs=[
    #         jobId
    #     ]
    # )
    # assert status == 'SUCCEEDED', pprint(job_response)
    # return job_response
