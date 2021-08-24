import aiohttp
from pyority_queue.heartbeat import *
from pyority_queue.enums.status_codes import *
from pyority_queue.errors.empty_queue_error import *


class Records:
    def __init__(self, job_type, task_type, base_url, logger):
        self.job_type = job_type
        self.task_type = task_type
        self.base_url = base_url
        self.logger = logger

    async def get_task(self, job_id, task_id):
        try:
            get_task_url = f'{self.base_url}/jobs/{job_id}/tasks/{task_id}'
            async with aiohttp.ClientSession() as session:
                self.logger.info(f'GET Request to: {get_task_url}.')
                async with session.get(get_task_url) as response:
                    resp = await response.json()
                    return resp
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')
            raise e

    async def consume(self, job_type, task_type):
        try:
            dequeue_url = f'{self.base_url}/tasks/{job_type}/{task_type}/startPending'
            async with aiohttp.ClientSession() as session:
                self.logger.info(f'consuming record.')
                headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
                async with session.post(dequeue_url, headers=headers) as response:
                    if response.status == StatusCodes.NOT_FOUND.value:
                        raise EmptyQueueError()
                    elif response.status == StatusCodes.OK.value:
                        return await response.json()
                    else:
                        raise Exception(response)
        except EmptyQueueError:
            self.logger.debug(f'consuming an record failed due to empty queue')
            pass
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')
            raise e

    async def update(self, job_id, task_id, payload):
        try:
            update_url = f'{self.base_url}/jobs/{job_id}/tasks/{task_id}'
            async with aiohttp.ClientSession() as session:
                self.logger.info(f'Update task: "{task_id}" request to {update_url}')
                headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
                async with session.put(update_url, json=payload, headers=headers) as response:
                    await response.text()
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')
            raise e
