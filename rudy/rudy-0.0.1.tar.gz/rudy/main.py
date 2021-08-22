import asyncio
import json
import sys

from nio import AsyncClient, RoomMessageText, MatrixRoom

import rudy.callbacks as callbacks

CONFIG_FILE = "config.json"

async def main() -> None:
  try:
    with open(CONFIG_FILE, "r") as f:
      config = json.load(f)
  except:
    print("Unable to load config file: {path}".format(path=CONFIG_FILE))
    sys.exit(1)

  client = AsyncClient(config['homeserver'])
  client.user_id      = config['user_id']
  client.device_id    = config['device_id']
  client.access_token = config['access_token']
  client.room_id      = config['room_id']
  client.add_event_callback(callbacks.message, RoomMessageText)

  await client.sync_forever(timeout=30000)
