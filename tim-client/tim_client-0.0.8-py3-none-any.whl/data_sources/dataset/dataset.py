from time import sleep
from pandas.core.frame import DataFrame
from typing import List, Union
from tim.core.credentials import Credentials
from tim.core.api import execute_request
from tim.types import Logs, Status, StatusResponse
from .types import CSVSeparator, DatasetListPayload, Dataset, DatasetListVersion, UploadCsvResponse, UploadCSVConfiguration


def __is_valid_csv_configuration(configuration: UploadCSVConfiguration) -> bool:
  if configuration is None: 
    return True

  if "csvSeparator" in configuration:
    return False

  if "workspaceId" in configuration:
    return False
  return True


def upload_csv(
    credentials: Credentials,
    dataset: DataFrame,
    configuration: UploadCSVConfiguration,
) -> UploadCsvResponse:
  if not __is_valid_csv_configuration(configuration):
    raise ValueError("Invalid configuration input.")

  configuration["csvSeparator"
               ] = CSVSeparator.SEMICOLON.value  # pyright: reportTypedDictNotRequiredAccess=false

  return execute_request(
      credentials=credentials,
      method="post",
      path="/datasets/csv",
      body=configuration,
      file=dataset.to_csv(sep=configuration["csvSeparator"], index=False),
  )


def get_version_status(credentials: Credentials, id: str, versionId: str) -> StatusResponse:
  return execute_request(
      credentials=credentials,
      method="get",
      path=f"/datasets/{id}/versions/{versionId}/status",
  )


def poll_dataset_version_status(
    credentials: Credentials, id: str, versionId: str, tries_left: int = 5
) -> StatusResponse:
  if tries_left < 1:
    raise ValueError("Timeout error.")

  response = get_version_status(credentials, id, versionId)
  if response['status'] == Status.FAILED.value:  # pyright: reportUnnecessaryComparison=false
    return response
  if response['status'] != Status.FINISHED.value and response['status'] != Status.FINISHED_WITH_WARNING.value:
    sleep(2)
    return poll_dataset_version_status(credentials, id, versionId, tries_left - 1)

  return response


def get_dataset(credentials: Credentials, id: str) -> Dataset:
  return execute_request(credentials=credentials, method="get", path=f"/datasets/{id}")


def get_dataset_logs(credentials: Credentials, id: str) -> List[Logs]:
  return execute_request(
      credentials=credentials,
      method="get",
      path=f"/datasets/{id}/log",
  )


def get_datasets(
    credentials: Credentials,
    offset: int,
    limit: int,
    workspaceId: Union[str, None] = None,
    sort: Union[str, None] = None
) -> List[Dataset]:

  payload = DatasetListPayload(offset=offset, limit=limit)
  if workspaceId: payload['workspaceId'] = workspaceId
  if sort: payload['sort'] = sort

  return execute_request(
      credentials=credentials, method='get', path=f'/datasets', params=payload
  )


def get_dataset_versions(credentials: Credentials, id: str, offset: int,
                         limit: int) -> List[DatasetListVersion]:
  return execute_request(
      credentials=credentials, method='get', path=f'/datasets/{id}/versions?offset={offset}&limit={limit}'
  )
