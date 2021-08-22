import random
from nio import AsyncClient, RoomMessageText, MatrixRoom

from rudy.data import NAMES, QUOTES


async def message_callback(self, room: MatrixRoom, event: RoomMessageText) -> None:
  # hack to avoid processing old messages at startup
  # todo: replace this once we have some sort of local state
  if (event.source['unsigned']['age'] > 5000):
    return

  if (event.body.upper().find(self.client.user_id.upper()) != -1):
    name  = random.choice(NAMES)

    # flip a coin
    if (event.body.upper().find('FLIP') != -1):
      quote = random.choice(['HEADS, {name}!','TAILS, {name}!'])

    # random quote
    else:
      quote = random.choice(QUOTES)

    await self.client.room_send(
      self.client.room_id,
      message_type="m.room.message",
      content={
        "msgtype": "m.text",
        "body": quote.format(name=name)
      }
    )
