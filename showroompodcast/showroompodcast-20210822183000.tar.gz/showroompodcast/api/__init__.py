"""SHOWROOM API."""
from abc import abstractmethod

import requests


class ShowroomApi:
    """Base class of SHOWROOM API."""

    USER_AGENT_WINDOWS_CHROME = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    @classmethod
    def request(cls, params):
        """
        To use connection pooling via session object
        to prevent NewConnectionError
        Failed to establish a new connection: [Errno -3] Temporary failure in name resolution
        # pylint: disable=line-too-long
        see: https://stackoverflow.com/questions/8356517/permanent-temporary-failure-in-name-resolution-after-running-for-a-number-of-h/8376268#8376268  # noqa: E501
        """
        session = requests.Session()
        session.headers.update({"User-Agent": ShowroomApi.USER_AGENT_WINDOWS_CHROME})
        response = session.get(url=cls.url(), params=params, timeout=20.0)
        response.raise_for_status()
        return response.json()

    @staticmethod
    @abstractmethod
    def url():
        raise NotImplementedError()  # pragma: no cover
