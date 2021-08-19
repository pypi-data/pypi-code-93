"""
Tracking module for Grid. Here we include logic
for tracking how users interact with the backend,
which helps us have a better picture of what the
complete user journey is across our product.

All of our tracking is done via the use of Segment
events. [1]

References
----------
[1] https://segment.com/docs/sources/server/python/
"""
from enum import Enum
import json
import os
import platform
import sys
import traceback
from typing import Dict
import uuid

import analytics
import click

from grid.cli.client import Grid
import grid.cli.globals as env
from grid.metadata import __version__


class TrackingEvents(Enum):
    EXCEPTION = 'EXCEPTION'
    CLI_STARTED = 'Cli started'
    CLI_FINISHED = 'Cli finished'
    RUN_CREATED = 'Run created'
    CONFIG_PARSED = 'Config parsed'
    INTERACTIVE_NODE_CREATED = 'Interactive node created'


class Segment:
    """Class for sending data to Grid's Segment analytics tracker."""
    client: analytics.Client

    def __init__(self, enabled=not env.GRID_DISABLE_TRACKING):
        """
        Initialize Segment tracking class

        Parameters
        ----------
        enabled: bool
            is the metric sending enabled
        """
        self.client = analytics.Client(
            write_key=env.SEGMENT_KEY,
            on_error=self.handle_error,
            send=enabled,
        )
        environment = {k: v for k, v in os.environ.items() if not self._is_env_sensitive(k)}
        self.client_kwargs = {
            'context': {
                'uname': platform.uname()._asdict(),
                'env': environment,
                'args': sys.argv,
                'cwd': os.getcwd(),
                'version': __version__,
                'invocation_id': str(uuid.uuid4()),
            },
        }
        self.client_kwargs['context']['json'] = json.dumps(self.client_kwargs['context'])
        user_id = None
        try:
            user_id = Grid().credentials.user_id
        except click.ClickException:
            pass

        anonymous_id = uuid.getnode()
        if user_id:
            self.client.alias(anonymous_id, user_id, **self.client_kwargs)
            self.client_kwargs['user_id'] = user_id
        else:
            self.client_kwargs['anonymous_id'] = anonymous_id

        self.client.identify(**self.client_kwargs)

    @staticmethod
    def _is_env_sensitive(key: str) -> bool:
        """
        Checks if the environment variable is sensitive for most common
        sensitive env vars

        Parameters
        ----------
        key: str
            environment key whose sensitivity we're checking

        Returns
        -------
            True if the env variable is sensitive, False otherwise


        """
        # covers GRID_API_KEY, AWS... etc
        for it in [
            "ACCESS",
            "KEY",
            "PASSWORD",
            "SECRET",
            "TOKEN",
        ]:
            if it in key.upper():
                return True
        return False

    @staticmethod
    def handle_error(error, items):  # pragma: no cover
        """
        Segment on_error callback
        """
        if env.DEBUG:
            env.logger.debug(f'Segment error detected: {error}')

    def send_event(self, event: TrackingEvents, properties: Dict = {}):
        """
        Send event happening to the Segment

        Parameters
        ----------
        event: TrackingEvents
            event which happened
        properties:
            Additional event properties
        """
        properties['json'] = json.dumps(properties)
        self.client.track(event=event.value, properties=properties, **self.client_kwargs)

    def report_exception(self, e: Exception):
        """
        report exception happening to the Segment backend
        Parameters
        ----------
        e: Exception

        """
        props = {
            'error': type(e).__name__,
            'stacktrace': traceback.format_stack(),
        }
        if hasattr(e, 'format_message'):
            props['message'] = e.format_message()
        elif hasattr(e, 'message'):
            props['message'] = e.message
        self.send_event(
            event=TrackingEvents.EXCEPTION,
            properties=props,
        )

    def flush(self):
        self.client.flush()
