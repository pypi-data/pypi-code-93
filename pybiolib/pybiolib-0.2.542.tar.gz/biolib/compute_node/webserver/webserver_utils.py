import time
from datetime import datetime
import requests

from biolib import utils
from biolib.typing_utils import Dict, List, Optional
from biolib.biolib_api_client import BiolibApiClient
from biolib.compute_node.webserver.worker_thread import WorkerThread
from biolib.compute_node.webserver import webserver_config
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger
from biolib.compute_node import enclave
from biolib.compute_node.enclave.parent_api_types import ComputeNodeInfo

JOB_ID_TO_COMPUTE_STATE_DICT: Dict = {}
UNASSIGNED_COMPUTE_PROCESSES: List = []


def finalize_and_clean_up_compute_job(job_id: str):
    JOB_ID_TO_COMPUTE_STATE_DICT.pop(job_id)

    if utils.BIOLIB_IS_RUNNING_IN_ENCLAVE and not utils.IS_DEV:
        logger.debug('Deregistering and shutting down...')
        enclave.ParentApi.deregister_and_shutdown()


def get_compute_state(unassigned_compute_processes):
    if len(unassigned_compute_processes) == 0:
        start_compute_process(unassigned_compute_processes)

    return unassigned_compute_processes.pop()


def start_compute_process(unassigned_compute_processes):
    compute_state = {
        'job_id': None,
        'status': {
            'status_updates': [
                {
                    'progress': 10,
                    'log_message': 'Initializing'
                }
            ],
        },
        'result': None,
        'attestation_document': b'',
        'received_messages_queue': None,
        'messages_to_send_queue': None,
        'worker_process': None
    }

    WorkerThread(compute_state).start()

    while True:
        if compute_state['attestation_document']:
            break
        time.sleep(1)

    unassigned_compute_processes.append(compute_state)


def validate_saved_job(saved_job):
    if 'app_version' not in saved_job['job']:
        return False

    if 'access_token' not in saved_job:
        return False

    if 'module_name' not in saved_job:
        return False

    return True


def report_availability(compute_node_info: ComputeNodeInfo):
    try:
        api_client = BiolibApiClient.get()
        logger.debug(f'Registering with {compute_node_info} to host {api_client.base_url} at {datetime.now()}')

        response: Optional[requests.Response] = None
        max_retries = 5
        for retry_count in range(max_retries):
            try:
                response = requests.post(f'{api_client.base_url}/api/jobs/report_available/', json=compute_node_info)
                break
            except Exception as error:  # pylint: disable=broad-except
                logger.error(f'Self-registering failed with error: {error}')
                if retry_count < max_retries - 1:
                    seconds_to_sleep = 1
                    logger.info(f'Retrying self-registering in {seconds_to_sleep} seconds')
                    time.sleep(seconds_to_sleep)

        if not response:
            raise BioLibError('Failed to register. Max retry limit reached')

        if response.status_code != 201:
            raise Exception("Non 201 error code")

        if response.json()['is_reserved']:
            # Start running job shutdown timer if reserved. It restarts when the job is actually saved
            enclave.ParentApi.start_shutdown_timer(webserver_config.COMPUTE_NODE_RUNNING_JOB_SHUTDOWN_TIME_MINUTES)

        else:
            # Else start the longer auto shutdown timer
            enclave.ParentApi.start_shutdown_timer(webserver_config.COMPUTE_NODE_AUTO_SHUTDOWN_TIME_MINUTES)

    except Exception as exception:  # pylint: disable=broad-except
        logger.error(f'Shutting down as self register failed due to: {exception}')
        if not utils.IS_DEV:
            enclave.ParentApi.deregister_and_shutdown()
