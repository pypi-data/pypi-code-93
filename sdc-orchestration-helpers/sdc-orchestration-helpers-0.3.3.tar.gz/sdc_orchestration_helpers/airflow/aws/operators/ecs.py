# pylint: disable=super-with-arguments
# pylint: disable=redefined-builtin
# pylint: disable=invalid-name

"""
    ECS TASK CODE
        - these are used in pythonOperator steps as a way \
            to flexibly call boto3 and perform any special requirements
"""
import logging
import time

import boto3
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)


class RunEcsTask(BaseOperator):
    """Run ECS Task Definition."""
    template_fields = ('config', 'xcom_tasks',)

    @apply_defaults
    def __init__(self, config=None, xcom_tasks=None, *args, **kwargs):
        super(RunEcsTask, self).__init__(*args, **kwargs)

        self.config = config
        self.xcom_tasks = xcom_tasks
        self.kwargs = kwargs

    def execute(self, context):
        """

        """
        CLIENT = boto3.client('ecs')

        # for multi_load where config is none, configs can be loaded from kwargs
        if self.config is not None:
            task_definition_name = self.config.get('task_definition_name')
            task_cluster = self.config.get('task_cluster')
            security_groups = self.config.get('security_groups')
            subnets = self.config.get('subnets')
        else:
            task_definition_name = self.kwargs.get('task_definition_name')
            task_cluster = self.kwargs.get('task_cluster')
            security_groups = self.kwargs.get('security_groups')
            subnets = self.kwargs.get('subnets')

        try:
            log_message = """
                Running task: {name} with configurations:
                ecs_task_cluster: {cluster}
                security_groups: {security_groups}
                subnets: {subnets}
                """.format(
                name=task_definition_name,
                cluster=task_cluster,
                security_groups=security_groups,
                subnets=subnets
            )
            logging.info(log_message)

            response = CLIENT.run_task(
                cluster=task_cluster,
                group=task_definition_name,
                launchType='FARGATE',
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'subnets': subnets,
                        'securityGroups': security_groups,
                        'assignPublicIp': 'ENABLED'
                    }
                },
                propagateTags='TASK_DEFINITION',
                taskDefinition=task_definition_name
            )

            logging.info(response)

            ecs_task_run_id = response['tasks'][0]['containers'][0]['taskArn'].split('/')[-1]
            context['task_instance'].xcom_push(
                key='task_run_id',
                value=ecs_task_run_id
            )

        except Exception as err:
            raise err


class MonitorEcsTask(BaseOperator):
    """Monitor ECS Task Definition status for Stopped."""
    template_fields = ('config', 'xcom_tasks',)

    @apply_defaults
    def __init__(self, config, xcom_tasks=None, *args, **kwargs):
        super(MonitorEcsTask, self).__init__(*args, **kwargs)

        self.config = config
        self.xcom_tasks = xcom_tasks

    def execute(self, context):
        """

        """
        CLIENT = boto3.client('ecs')

        task_cluster = self.config.get('task_cluster', None)
        task_run_id = self.config.get('task_run_id', None)

        task_ids = self.xcom_tasks['task_run_id']['task_id']

        if task_run_id is None:
            # if optional config task_run_id is None, pull from xcom
            task_run_id = context['task_instance'].xcom_pull(
                task_ids=task_ids,
                key=self.xcom_tasks['task_run_id']['key']
            )

        try:
            logging.info('Looking for ECS Task ID: {id} in Cluster: {cluster}'.format(
                id=task_run_id, cluster=task_cluster)
            )

            response = CLIENT.describe_tasks(
                cluster=task_cluster,
                tasks=[task_run_id]
            )['tasks']

            logging.info('Response Data: {response}'.format(
                response=response
            ))

            while True:
                ecs_task_definition_status = response[0]['containers'][0].get('lastStatus')

                logging.info('Task Status: {status}.'.format(status=ecs_task_definition_status))
                if ecs_task_definition_status == 'STOPPED':
                    return None

                time.sleep(10)

        except Exception as err:
            raise err
