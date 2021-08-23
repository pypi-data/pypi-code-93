import asyncio
import json
import logging
import sys

from pysnmp.hlapi.asyncio import SnmpEngine

from prtg_pyprobe.communication.communication_http_api import PRTGHTTPApi
from prtg_pyprobe.monitoring import monitoring
from prtg_pyprobe.utils.config import ProbeConfig
from prtg_pyprobe.utils.defaults import CONFIG_PATH
from prtg_pyprobe.utils.logging import setup_logging, setup_file_logging
from prtg_pyprobe.utils.sensor_loader import create_sensor_objects


async def monitoring_loop(
    prtg_api: PRTGHTTPApi, sensors: list, snmp_eng: SnmpEngine, run_monitoring: bool, config: dict
):
    """The monitoring functionality of the pyprobe.

    Args:
        prtg_api (PRTGHTTPApi): PRTGHTTPApi object.
        sensors (list): List of sensor objects.
        snmp_eng (SnmpEngine): SNMP Engine object.
        run_monitoring (bool): Bool which determines whether to run monitoring or not.
        config (dict): Probe configuration as dict.

    """
    while run_monitoring:
        tasks_api_response = await prtg_api.get_tasks()
        if tasks_api_response.status_code == 200:
            tasks = tasks_api_response.json()
            logging.debug(f"Tasks received from PRTG {tasks}")
            if len(tasks) > 0:
                await monitoring.monitoring(
                    tasks_list=tasks,
                    sensor_objects=sensors,
                    snmp_engine=snmp_eng,
                    prtg_api=prtg_api,
                    config=config,
                )
        if tasks_api_response.status_code == 401:
            logging.warning("Please check that your probe has been approved in PRTG!")
        if await asyncio.sleep(10):
            break


def main():
    """The pyprobe main function."""
    logger, console_handler, formatter = setup_logging()
    logger.info("Starting pyprobe!")
    try:
        logger.info("Loading configuration")
        cfg = ProbeConfig(path=f"{CONFIG_PATH}config.yml").read()
    except FileNotFoundError:
        logger.exception("No configuration file found, ending.")
        sys.exit(1)

    # noinspection PyBroadException
    try:
        if not cfg["log_file_location"] == "":
            setup_file_logging(cfg, logger, formatter, console_handler)
            logger.info("Now logging to your logfile")
        logger.setLevel(cfg["log_level"])
    except Exception:
        logger.exception("Something bad happened!")
        sys.exit(1)

    logger.info("Config loaded and probe announcing to PRTG")
    logger.debug(f"Your current config: \n {json.dumps(cfg, indent=2)}")

    logger.info("Initializing SNMP Engine")
    snmp_eng = SnmpEngine()

    logger.info("Initializing PRTG API")
    prtg_api = PRTGHTTPApi(probe_config=cfg, backoff_factor=10)
    logger.info("Initializing Sensors")
    sensors = create_sensor_objects()
    sensor_defs = [sensor.definition for sensor in sensors]
    logger.info("Init done!")
    send_announce = True
    run_monitoring = False
    while send_announce:
        announce_api_response = prtg_api.send_announce(sensor_definitions=sensor_defs)
        if announce_api_response.status_code == 200:
            send_announce = False
            run_monitoring = True
    monitoring_event_loop = asyncio.get_event_loop()
    monitoring_event_loop.run_until_complete(
        monitoring_loop(
            prtg_api=prtg_api,
            sensors=sensors,
            snmp_eng=snmp_eng,
            run_monitoring=run_monitoring,
            config=cfg,
        )
    )


if __name__ == "__main__":
    main()
