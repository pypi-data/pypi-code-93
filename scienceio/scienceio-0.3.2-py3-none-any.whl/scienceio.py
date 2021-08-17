import configparser
import enum
import json
import requests
import types
import typing as tp
from pathlib import Path

CONFIG = types.SimpleNamespace(
    BIONLP_API_URL='https://bionlp.aws.science.io/v1',
    HELP_EMAIL="api-help@science.io",
    SETTINGS_FILE_PATH=Path.home() / ".scio" / "config",
    SETTINGS_TEMPLATE="[SETTINGS]" \
                      "email=your@email.com"
)


class ScienceIOError(Exception):
    """Base class for all exceptions that are raised by the ScienceIO SDK."""


class TimeoutError(ScienceIOError):
    """Raised when a call to the ScienceIO API times out."""

    def __init__(self, msg):
        self.msg = msg


class ResponseFormat(str, enum.Enum):
    JSON = 'application/json'

    def format_response(self, response):
        if self is ResponseFormat.JSON:
            return response.json()
        else:
            raise NotImplementedError('unknown response format')

    def create_headers(self) -> tp.Dict:
        return {
            'Content-Type': self.value
        }


class ScienceIO(object):
    def __init__(self,
                 response_format: ResponseFormat = ResponseFormat.JSON,
                 timeout: tp.Optional[tp.Union[int, float]] = 1200,
                 ):
        """Initializer for the ScienceIO client.

        Args:
            email:
                The user's login/email address.
            response_format:
                Format to use for responses (default: `ResponseFormat.JSON`).
            timeout:
                Amount of time to wait before timing out network calls, in seconds.
                If `None`, timeouts will be disabled. (default: 1200)
        """

        self.response_format = response_format
        self.timeout = timeout

        # API endpoints to use.
        self.bionlp_url = CONFIG.BIONLP_API_URL

        # Create a persistent session across requests.
        # https://docs.python-requests.org/en/master/user/advanced/
        self.session = requests.Session()
        self.session.params = {}

        # Read config file
        config = configparser.RawConfigParser()
        config.read(CONFIG.SETTINGS_FILE_PATH)

        try:
            email = config["SETTINGS"]["email"]
        except KeyError:
            print(f"Could not read {str(CONFIG.SETTINGS_FILE_PATH)}")
            return

        self.email = email

    @staticmethod
    def register(
            first_name: str,
            last_name: str,
            email: str,
            response_format: ResponseFormat = ResponseFormat.JSON
    ) -> tp.Dict:
        """
        Creates a new Scienceio user account.

        Args:
            `user_info`: Profile and login information for the new user

        Returns:
            Dictionary containing information about the newly-created user,
            including the new user id.
        """
        body = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        }

        try:
            response = requests.post(f'{CONFIG.BIONLP_API_URL}/register',
                                     json=body)
        except requests.Timeout:
            # NOTE: The `from None` disables the "during handling of the above exception,
            #       another exception occurred"-chain. It can be removed if we're OK with
            #       exposing some SDK internals.
            raise TimeoutError('user registration timed out, please try again') from None

        response.raise_for_status()

        if response.status_code == 200:
            return "Successful registration, an email was sent to you to verify your email."

        return response_format.format_response(response)

    def annotate(self, text: str):
        if not isinstance(text, str):
            raise ValueError("annotate argument must be a string.")

        payload = json.dumps({
            "text": text,
            "email": self.email,
        })

        headers = self.response_format.create_headers()
        target_url = f'{self.bionlp_url}/annotate'

        try:
            response = self.session.post(
                target_url,
                data=payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.Timeout:
            raise TimeoutError('annotation timed out, please try again') from None

        return self.response_format.format_response(response)
