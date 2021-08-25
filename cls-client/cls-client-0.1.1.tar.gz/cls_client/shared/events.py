import sys
import json
import urllib.request, urllib.error

from .settings import settings
from .logger import logger

# https://stackoverflow.com/a/35904211/1110798
this = sys.modules[__name__]
this.events_pending = []
this.events_sent = []
this.events_failed = []
# TODO use a log instead?


def track_event(slug, type, metadata={}):
    data = {
        "slug": slug,
        "type": type,
        "metadata": metadata,
        "invocation_id": settings.invocation_id,
    }

    if not settings.should_track(event_data=data):
        return

    this.events_pending.append(data)

    logger.debug(f"CLS event added slug={slug} type={type}")


def dispatch_events():
    if not settings.get_project_key():
        raise Exception("CLS project key not set")

    # TODO batch create

    for data in this.events_pending:
        req = urllib.request.Request(
            settings.get_api_url("events"),
            data=json.dumps(data, default=lambda o: "<serialization error>").encode(
                "utf-8"
            ),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Token " + settings.get_project_key(),
            },
        )
        try:
            response = urllib.request.urlopen(req)
            logger.debug("CLS events dispatched")
            logger.debug(response.read().decode("utf-8"))
            this.events_sent.append(data)  # Keep a record that can be debugged
        except (urllib.error.HTTPError, urllib.error.urllib.error.URLError) as e:
            logger.debug(f"CLS event submission failed: {e}")
            this.events_failed.append(data)

    this.events_pending = []
