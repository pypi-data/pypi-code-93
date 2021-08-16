import logging
from typing import Dict, List, Any

import httpx

from peach_collector import __version__
from peach_collector._utils import timestamp, check_event

logger = logging.getLogger(__name__)


class PeachCollector:
    def __init__(
        self,
        site_key: str,
        app_id: str,
        server_url: str = "https://pipe-collect.ebu.io/v3/collect",
        enabled: bool = True,
        debug: bool = True,
    ):
        self.site_key = site_key
        self.app_id = app_id
        self.server_url = server_url
        self.enabled = enabled
        self.debug = debug
        self.events: List[Dict[str, Any]] = []

        if self.enabled:
            assert self.server_url and self.app_id and self.site_key

    def add_event(self, event: Dict[str, Any]):
        self.events.append(check_event(event))

    async def send_events(self):

        if not self.events:
            logger.info("No events to send")
            return

        payload = {
            "peach_schema_version": "1.0.3",
            "peach_implementation_version": __version__,
            "sent_timestamp": timestamp(),
            "client": {"type": "web", "app_id": self.app_id},
            "events": self.events,
        }

        if self.debug:
            logger.info(payload)

        if not self.enabled:
            logger.info(
                f"Peach collector is disabled. Would have sent {len(self.events)} events to peach"
            )
            self.events = []
            return

        logger.info(
            f"Sending {len(self.events)} events. Url: {self.server_url}. App id: {self.app_id}"
        )
        async with httpx.AsyncClient() as client:
            res = await client.post(self.server_url, params={"s": self.site_key}, json=payload)
            res.raise_for_status()
        self.events = []

    def __call__(self):
        self.send_events()
