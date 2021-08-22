# -*- coding: utf-8 -*-

import sys

from metalmetrics.cmd.argument import Argument
from metalmetrics.cmd.banner import BANNER
from metalmetrics.config.config import Config, ConfigException
from metalmetrics.flow.flow import Flow, FlowException
from metalmetrics.logger.logger import Logger
from metalmetrics.metrics.metrics import Metrics, MetricsException
from metalmetrics.queue.queue import Queue, QueueException


def main():
    print(BANNER)

    argument = Argument()
    arg = argument.parse(sys.argv)

    try:
        config = Config()
        config.config_file = arg.config_file
        config.inxi_file = arg.inxi_file
        config.listen_url = arg.listen_url
        config.output_file = arg.output_file
    except ConfigException as e:
        Logger.error(str(e))
        return -1

    try:
        metrics = Metrics(config)
    except MetricsException as e:
        Logger.error(str(e))
        return -2

    Logger.info("metrics running")

    if len(config.listen_url) != 0:
        try:
            flow = Flow(config)
            flow.run(metrics.routine)
        except FlowException as e:
            Logger.error(str(e))
            return -3
    else:
        try:
            queue = Queue(config)
            queue.run(metrics.routine)
        except QueueException as e:
            Logger.error(str(e))
            return -4

    Logger.info("metrics exiting")

    return 0
