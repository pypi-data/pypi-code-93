from tim.core.api import execute_request
from tim.core.credentials import Credentials
from .types import UseCaseConfiguration, CreateUseCaseResponse


def create_use_case(credentials: Credentials, configuration: UseCaseConfiguration) -> CreateUseCaseResponse:
  return execute_request(credentials=credentials, method='post', path='/use-cases', body=configuration)
