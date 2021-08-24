from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Union
import uuid

import grpc
import jwt


@dataclass(unsafe_hash=True)
class Credentials:
    user_id: str
    api_key: str

    @classmethod
    def from_locale(cls) -> "Credentials":
        """Instantiates the credentials using implicit locale.

        First use environment variables, otherwise look for credentials stored in file.

        Returns
        -------
        Credentials
            instantiated credentials object.
        """
        # if user has environment variables, use that
        user_id = os.getenv('GRID_USER_ID')
        api_key = os.getenv('GRID_API_KEY')
        if user_id and api_key:
            return cls(user_id=user_id, api_key=api_key)

        # otherwise overwrite look for credentials stored locally as a file
        if os.getenv("CI"):
            p = Path.home() / ".grid" / "credentials.json"
        else:
            p = Path(os.getenv('GRID_CREDENTIAL_PATH', Path.home() / ".grid" / "credentials.json"))

        if not p.exists():
            raise PermissionError('No credentials available. Did you login?')
        with p.open() as f:
            credentials = json.load(f)

        return cls(
            user_id=credentials['UserID'],
            api_key=credentials['APIKey'],
        )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Credentials":
        """Instantiates the credentials using specified file path.

        Parameters
        ----------
        path
            file path to the config yaml or json on disk.

        Returns
        -------
        Credentials
            instantiated credentials object.
        """
        p = Path(path).absolute()
        if not p.exists():
            raise PermissionError('No credentials available. Did you login?')
        with p.open() as f:
            credentials = json.load(f)

        return cls(
            user_id=credentials['UserID'],
            api_key=credentials['APIKey'],
        )


class GrpcAuth(grpc.AuthMetadataPlugin):
    def __init__(self, credentials: "Credentials"):
        self._creds = credentials

    @property
    def _bearer_token(self) -> str:
        if os.getenv("GRID_AUTH_TOKEN"):
            return os.getenv("GRID_AUTH_TOKEN")

        dt_now = datetime.utcnow()
        # TODO(rusenask): Delete this when you migrate everything to nice JWTs
        token = jwt.encode(
            payload={
                "aud": ["grid"],
                "exp": dt_now + timedelta(seconds=30),
                "iat": dt_now,
                "iss": "grid-cli",
                "jti": str(uuid.uuid4()),
                "nbf": dt_now,
                "sub": self._creds.user_id
            },
            key=self._creds.api_key,
            algorithm="HS256"
        )

        return token.decode("ascii")

    def __call__(self, context: "grpc.AuthMetadataContext", callback: "grpc.AuthMetadataPluginCallback") -> None:
        callback((('authorization', f"Bearer {self._bearer_token}"), ), None)
