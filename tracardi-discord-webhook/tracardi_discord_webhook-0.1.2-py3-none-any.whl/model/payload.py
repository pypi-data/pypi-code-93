from pydantic import BaseModel


class DiscordPayload(BaseModel):
    content: str
    username: str = None
