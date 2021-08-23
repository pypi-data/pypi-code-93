from pydantic import AnyHttpUrl, BaseModel


class ZapierWebHookConfiguration(BaseModel):
    url: AnyHttpUrl
    timeout: int = 10

