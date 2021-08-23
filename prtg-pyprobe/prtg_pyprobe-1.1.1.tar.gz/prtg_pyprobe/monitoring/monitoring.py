import asyncio
import itertools
import logging

from pysnmp.hlapi.asyncio import SnmpEngine

from prtg_pyprobe.communication.communication_http_api import PRTGHTTPApi


async def run_monitoring_tasks(
    sensors_avail: list,
    taskdata: list,
    prtg_api: PRTGHTTPApi,
    snmp_engine: SnmpEngine,
    async_queue: asyncio.Queue,
    config: dict,
):
    """Matches tasks to sensors and does the acutal monitoring.

    Args:
        sensors_avail (list): List of available sensors.
        taskdata (list): List of tasks from the PRTG Core.
        prtg_api (PRTGHTTPApi): A PRTG HTTP API object.
        snmp_engine (SnmpEngine): SNMP Engine object.
        async_queue (asyncio.Queue): An AsyncIO Queue.
        config (dict): The probe config as dict.

    """
    monitoring_task_list = []
    task_chunk_size = int(config["probe_task_chunk_size"])
    task_chunks = [taskdata[x : x + task_chunk_size] for x in range(0, len(taskdata), task_chunk_size)]
    for chunk in task_chunks:
        for sensor, task in itertools.product(sensors_avail, chunk):
            if task["kind"] == sensor.kind:
                if "mpsnmp" in task["kind"]:
                    monitoring_task_list.append(
                        asyncio.create_task(sensor.work(task_data=task, q=async_queue, snmp_engine=snmp_engine))
                    )
                else:
                    monitoring_task_list.append(asyncio.create_task(sensor.work(task_data=task, q=async_queue)))
        logging.info(f"Current Queue Size: {async_queue.qsize()}")

        logging.debug(f"Running Tasks in Event Loop (before join): {asyncio.all_tasks()}")
        await asyncio.gather(*monitoring_task_list)
        results = []
        while not async_queue.qsize() == 0:
            results.append(await async_queue.get())
        [mt.cancel() for mt in monitoring_task_list]
        logging.debug(f"Running Tasks in Event Loop (after join): {asyncio.all_tasks()}")
        chunk_response = await prtg_api.send_data(sensor_response_data=results)
        if chunk_response.status_code == 200:
            logging.info("Monitoring data successfully sent to PRTG Core.")


async def monitoring(
    tasks_list: list, sensor_objects: list, prtg_api: PRTGHTTPApi, snmp_engine: SnmpEngine, config: dict
):
    """
    An additional wrapper around ``run_monitoring_tasks``
    Args:
        tasks_list (list):
        sensor_objects (list):
        prtg_api (PRTGHTTPApi): A PRTG HTTP API object.
        snmp_engine (SnmpEngine): SNMP Engine object.
        config (dict):

    Returns:
        list: A list of monitoring results

    """
    logging.info("Initializing Queue")
    async_queue = asyncio.Queue()

    res = await run_monitoring_tasks(
        sensors_avail=sensor_objects,
        taskdata=tasks_list,
        snmp_engine=snmp_engine,
        async_queue=async_queue,
        prtg_api=prtg_api,
        config=config,
    )
    logging.debug(f"Running Tasks in Event Loop (after results): {asyncio.all_tasks()}")
    return res
