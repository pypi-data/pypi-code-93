"""
    Athena Sensors
    Used for Monitoring tasks run on athena
    In practice any tasks that have a execution time which could be length or uncertain.
"""
import logging
import boto3
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(None)

class MonitorQueryExecution(BaseSensorOperator):
    template_fields = ('query_execution_id', 'poke_interval', 'timeout', 'soft_fail', 'mode', 'xcom_tasks')

    @apply_defaults
    def __init__(
        self,
        query_execution_id=None,
        poke_interval=60,
        timeout=60 * 60 * 24 * 7,
        soft_fail=False,
        mode='poke',
        xcom_tasks=None,
        *args, **kwargs
    ):

        super(MonitorQueryExecution, self).__init__(
            poke_interval=poke_interval,
            timeout=timeout,
            soft_fail=soft_fail,
            mode=mode,
            *args,
            **kwargs
        )
        self.query_execution_id = query_execution_id
        self.xcom_tasks = xcom_tasks
    
    def poke(self, context):
        """
            Runs athena query against feature store
            https://sagemaker.readthedocs.io/en/stable/api/\
                prep_data/feature_store.html#sagemaker.feature_store.feature_group.AthenaQuery
        """
        # init boto session and sagemaker
        BOTO_SESSION = boto3.Session()
        ATHENA_CLIENT = BOTO_SESSION.client('athena')
        try:
            if self.query_execution_id is None:
                self.query_execution_id = context['task_instance'].xcom_pull(
                    task_ids=self.xcom_tasks['query_execution_id']['task_id'],
                    key=self.xcom_tasks['query_execution_id']['key']
                )
                assert self.query_execution_id is not None, (
                    "No {xcom_key} found in upstream={task_ids} task. "
                    "Either hardcode in config or pass from previous job".format(
                        xcom_key=self.xcom_tasks['query_execution_id']['key'],
                        task_ids=self.xcom_tasks['query_execution_id']['task_id']
                    )
                )
            logging.info("With query_id = {}\n".format(self.query_execution_id))
            # loop while results completing
            # on complete, do training next
            response = ATHENA_CLIENT.get_query_execution(
                QueryExecutionId=self.query_execution_id
            )
            query_execution_response = response.get('QueryExecution', {})
            job_state = query_execution_response.get('Status', {}).get('State', None)
            reason = query_execution_response.get('Status', {}).get('StateChangeReason', None)
            output_location = query_execution_response.get('ResultConfiguration', {}).get('OutputLocation', None)
            # push response up
            context['task_instance'].xcom_push(
                key='output_location',
                value=output_location
            )
            logger.info("Job status = {}".format(job_state))
            if job_state == 'SUCCEEDED':
                return True
            elif job_state in ['QUEUED', 'RUNNING']:
                # retry on failure
                return False
            else:
                # retry on failure, eventually fail
                raise Exception(
                    "query status == {JOB_STATE} with reason = {REASON}".format(
                        JOB_STATE=job_state, REASON=reason
                    )
                )
                
        except Exception as err:
            raise
