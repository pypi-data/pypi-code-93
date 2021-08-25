from json.decoder import JSONDecodeError

import requests
from biolib.typing_utils import Optional
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


class _ApiClient:
    def __init__(self, base_url: str):
        self.base_url: str = base_url
        self.refresh_token: Optional[str] = None
        self.access_token: Optional[str] = None

    @property
    def is_signed_in(self) -> bool:
        return self.refresh_token is not None and self.access_token is not None

    def login(self, api_token: Optional[str], exit_on_failure=False):
        if not api_token:
            if exit_on_failure:
                raise BioLibError('Error: Attempted login, but BIOLIB_TOKEN was not set, exiting...')
            else:
                logger.debug('Attempted login, but BIOLIB_TOKEN was not set, so continuing without logging in')
                return

        response = requests.post(
            f'{self.base_url}/api/user/api_tokens/exchange/',
            json={'token': api_token},
        )
        try:
            json_response = response.json()
        except JSONDecodeError as error:
            logger.error('Could not decode response from server as JSON:')
            raise BioLibError(response.text) from error
        if not response.ok:
            logger.error('Login with API token failed:')
            raise BioLibError(json_response['detail'])
        else:
            self.refresh_token = json_response['refresh_token']
            self.access_token = json_response['access_token']
            logger.info('Successfully authenticated')


class BiolibApiClient:
    api_client: Optional[_ApiClient] = None

    @staticmethod
    def initialize(base_url: str):
        BiolibApiClient.api_client = _ApiClient(base_url)

    @staticmethod
    def get() -> _ApiClient:
        if BiolibApiClient.api_client is not None:
            return BiolibApiClient.api_client
        else:
            raise BioLibError('Attempted to use uninitialized API client')
