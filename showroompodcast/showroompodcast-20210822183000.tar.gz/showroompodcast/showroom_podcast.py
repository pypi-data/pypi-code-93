"""Main module."""
import asyncio
import logging
from pathlib import Path

from asynccpu import ProcessTaskPoolExecutor

from showroompodcast import CONFIG
from showroompodcast.archiving_task_manager import ArchivingTaskManager
from showroompodcast.showroom_archiver import TIME_TO_FORCE_TARMINATION, ShowroomArchiver
from showroompodcast.showroom_poller import ShowroomPoller
from showroompodcast.slack.slack_client import SlackNotification


class ShowroomPodcast:
    """Main class."""

    def __init__(
        self, *, path_to_configuraion: Path = None, time_to_force_termination: int = TIME_TO_FORCE_TARMINATION
    ) -> None:
        logging.basicConfig(level=logging.DEBUG)
        CONFIG.load(path_to_configuraion)
        self.showroom_archiver = ShowroomArchiver(time_to_force_termination=time_to_force_termination)
        self.archiving_task_manager = ArchivingTaskManager(CONFIG.list_room_id)
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Runs"""
        try:
            asyncio.run(self.archive_repeatedly())
        except Exception as error:
            self.logger.exception(error)
            if CONFIG.slack.bot_token is not None and CONFIG.slack.channel is not None:
                SlackNotification(CONFIG.slack.bot_token, CONFIG.slack.channel).post_error(error)
            raise error

    async def archive_repeatedly(self):
        with ProcessTaskPoolExecutor(max_workers=CONFIG.number_process, cancel_tasks_when_shutdown=True) as executor:
            showroom_poller = ShowroomPoller(self.showroom_archiver, executor)
            while True:
                await self.archiving_task_manager.poll_all_rooms(showroom_poller)
