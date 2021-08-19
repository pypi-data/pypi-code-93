from io import StringIO
import pandas as pd
from time import sleep
from typing import Optional, List
from tim.core import Credentials
from tim.core.api import execute_request
from tim.core.credentials import Credentials
from tim.types import Logs, Status, StatusResponse
from .types import BuildModelResponse, ForecastAccuracies, ForecastModelResult, ForecastJobConfiguration, ExecuteResponse, ForecastMetadata, ForecastTableRequestPayload


def build_model(credentials: Credentials, job_configuration: ForecastJobConfiguration) -> BuildModelResponse:
  return execute_request(
      credentials, method='post', path='/forecast-jobs/build-model', body=job_configuration
  )


def execute(credentials: Credentials, id: str) -> ExecuteResponse:
  return execute_request(credentials=credentials, method='post', path=f'/forecast-jobs/{id}/execute')


def get_status(credentials: Credentials, id: str) -> StatusResponse:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}/status')


def get_forecast(credentials: Credentials, id: str) -> ForecastMetadata:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}')


def get_forecast_table_results(
    credentials: Credentials, id: str, forecastType: Optional[str] = None, modelIndex: Optional[int] = None
) -> pd.DataFrame:
  payload = ForecastTableRequestPayload(forecastType=forecastType, modelIndex=modelIndex)

  response = execute_request(
      credentials=credentials, method='get', path=f'/forecast-jobs/{id}/results/table', params=payload
  )

  data_string = StringIO(response)

  return pd.read_csv(data_string)  # pyright: reportGeneralTypeIssues=false, reportUnknownMemberType=false


def get_forecast_model_results(credentials: Credentials, id: str) -> ForecastModelResult:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}/results/model')


def get_forecast_accuracies_result(credentials: Credentials, id: str) -> ForecastAccuracies:
  return execute_request(
      credentials=credentials, method='get', path=f'/forecast-jobs/{id}/results/accuracies'
  )


def get_forecast_logs(credentials: Credentials, id: str) -> List[Logs]:
  return execute_request(credentials=credentials, method='get', path=f'/forecast-jobs/{id}/log')


def poll_forecast_status(credentials: Credentials, id: str, tries_left: int = 150) -> StatusResponse:
  if tries_left < 1:
    raise ValueError("Timeout error.")

  response = get_status(credentials, id)
  if Status(response['status']).value == Status.FAILED.value:
    return response
  if Status(response['status']).value != Status.FINISHED.value and Status(
      response['status']
  ).value != Status.FINISHED_WITH_WARNING.value:
    sleep(2)
    return poll_forecast_status(credentials, id, tries_left - 1)

  return response
