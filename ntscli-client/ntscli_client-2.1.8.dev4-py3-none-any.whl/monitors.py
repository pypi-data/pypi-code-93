import json
import threading
from threading import Event
from typing import Optional, TextIO

from kaiju_mqtt_py import MqttPacket
from ntscli_cloud_lib.automator import StatusBody
from ntscli_cloud_lib.status_watcher_interface import StatusWatcherInterface
import requests

# Implementation libs
from ntsjson.functions import nonblock_target_write
from ntsjson.log import logger


class BlockMainThreadUntilCompleteMonitor(StatusWatcherInterface):
    """
    A class sets a threading.Event when a test plan run completes.
    """

    def __init__(self):
        self.finished = Event()

    def handle_progress_update(self, packet: MqttPacket):
        """
        Handle updates for progress from the runner.

        This is a convenience function. The JSON payload is converted to a dict and passed to this function
        to save the clients from having to deal with all the assorted logic.

        This gets an MqttPacket - which is an object with attributes .topic and .payload.
        The payload includes the target, which is especially useful if testing multiple devices behind one RAE.

        The easiest way to deal with the payload is to convert it to an object:
        casted: StatusBody = StatusBody().from_dict(value=packet.payload)
            if casted.data.step is not None:
                myevent.set()

        'status' is nearly always one of these:
        running, pending, passed, failed, cancelled, invalid

        Additional fields will stop being None as they are populated by the test and Automator.
        Additional classes can be added to give you multiple abilities/outputs. Just remember they are not in threads,
        so don't do slow things. Set up your own threaded workers, etc. unlike what I do elsewhere in this sample.

        :param packet:
        :return:
        """

    def handle_run_complete(self, packet: MqttPacket):
        """
        When the run is no longer active, you get one final update message.

        This gets an MqttPacket - which is an object with attributes .topic and .payload.

        The easiest way to deal with the payload is to convert it to a CloudStatus object:
        casted = CloudStatus().from_dict(value=packet.payload)
        The CloudStatus fields can tell you which device and where to download the full JSON report
        of the test plan.

        :param packet:
        :return:
        """
        self.finished.set()


class PrintResultsWhenDoneClass(StatusWatcherInterface):
    """
    Just print at the end.

    This does not block the process from exiting, so use it with the DoneWaitingClass.
    """

    def __init__(self, result_file: TextIO, skip_download: bool = True):
        self.my_thread: Optional[threading.Thread] = None
        self.skip_download: bool = skip_download
        self.result_file: TextIO = result_file

    def handle_progress_update(self, packet: MqttPacket):
        """Can't be bothered."""

    def handle_run_complete(self, packet: MqttPacket):
        """Download and print the results from the remote url."""
        raw = packet.payload
        casted: StatusBody = StatusBody().from_dict(value=packet.payload)

        if self.skip_download:
            result_str = json.dumps(raw, indent=4)
            if self.result_file:
                nonblock_target_write(self.result_file, result_str)
        else:
            if casted.running:
                logger.error("Not downloading full result set because the batch is still running.")
            else:
                if casted.results_url is None:
                    return

                logger.info("Downloading full report from URL in JSON response")
                # grab and unzip the url
                resp2 = requests.get(casted.results_url)
                try:
                    resp2.raise_for_status()
                except requests.HTTPError:
                    logger.error(
                        "We couldn't download the file for you because the temporary URL expired. You can still find results on NTS. "
                        "Continuing analysis."
                    )
                    return

                if self.result_file:
                    full_result_set: StatusBody = StatusBody().from_dict(value=resp2.json())
                    nonblock_target_write(self.result_file, full_result_set.to_json(indent=4))


class PrintResultsWhileRunningClass(StatusWatcherInterface):
    """
    Download result files as soon as you see the report come in instead of waiting.

    This does not block the process from exiting, so use it with the DoneWaitingClass.
    """

    def __init__(self, result_file: TextIO):
        self.result_file: TextIO = result_file

    def handle_progress_update(self, packet: MqttPacket):
        """Download and print the results from the remote url only while running."""
        nonblock_target_write(self.result_file, json.dumps(packet.payload, indent=4))

    def handle_run_complete(self, packet: MqttPacket):
        """Can't be bothered."""
