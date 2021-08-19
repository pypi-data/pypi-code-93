from dataclasses import dataclass


@dataclass(frozen=True)
class AuthInfo:
    email_address: str
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str
