from pydantic import AnyHttpUrl, BaseModel


class DiscordWebHookConfiguration(BaseModel):
    url: AnyHttpUrl
    timeout: int = 10

