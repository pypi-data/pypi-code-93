import json
import logging
from pathlib import Path

import httpx

from .common import DEFAULT_CONFIG_FILENAME, load_yaml
from .wsgi import load_app, patch_response

logger = logging.getLogger(__name__)


async def call_app(app, event):
    host_url = event["headers"].get("Host", "https://raw-function.net")
    if not host_url.startswith("http"):
        host_url = f"https://{host_url}"
    async with httpx.AsyncClient(app=app,
                                 base_url=host_url) as client:
        request = client.build_request(
            method=event["httpMethod"],
            url=event["url"],
            headers=event["headers"],
            params=event["queryStringParameters"],
            json=json.load(event["body"]) if event["body"] else None,
        )
        response = await client.send(request)
        return response


try:
    config = load_yaml(Path(Path(__file__).resolve().parent.parent,
                            DEFAULT_CONFIG_FILENAME))

    app = load_app(config.get("entrypoint"),
                   config.get("DJANGO_SETTINGS_MODULE"))
except ValueError:
    logger.warning("Looks like broken Yappa config is used")


async def handle(event, context):
    if not event:
        return {
            'statusCode': 500,
            'body': "got empty event",
        }
    response = await call_app(app, event)
    return patch_response(response)
