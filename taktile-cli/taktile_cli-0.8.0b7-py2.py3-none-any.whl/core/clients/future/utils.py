import math
import typing as t
from http import HTTPStatus

import pandas as pd  # type: ignore
import requests
import tenacity  # type: ignore
from pyarrow import Table  # type: ignore
from pyarrow.flight import FlightClient  # type: ignore
from pyarrow.flight import ActionType, FlightDescriptor
from requests import ConnectionError, Timeout

from tktl.core.clients.future.http import API
from tktl.core.config import settings
from tktl.core.exceptions.exceptions import (
    APIClientException,
    APIClientExceptionRetryable,
    APISwitchException,
)
from tktl.core.loggers import LOG
from tktl.core.serializers import deserialize_arrow, serialize_arrow

# codes for which retry-ing is not necessary, and for which
# precise error information can be retrieved either from
# the request, or deployment logs
DO_NOT_RETRY_STATUS_CODES = [
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.UNAUTHORIZED,
    HTTPStatus.UNPROCESSABLE_ENTITY,
]


def safe_post(
    *, api: API, url: str, json: t.Any, retries: int = 3, timeout: float = 10.0
):
    """safe_post.
    HTTP POST request with retrying

    Parameters
    ----------
    api : API
        the underlying api
    url : str
        url to make the request to
    json: t.Any
        data to be sent
    retries : int
        retries
    timeout : float
        timeout
    """

    def my_after(retry_state):
        LOG.warning(
            f"Timeout while trying to call endpoint on try #{retry_state.attempt_number}/{retries}: {retry_state.outcome}"
        )

    def my_stop(retry_state):
        if retry_state.attempt_number >= retries:
            LOG.error(
                f"Giving up trying to call endpoint after {retry_state.attempt_number} attempts"
            )
            return True
        return False

    @tenacity.retry(
        stop=my_stop,
        retry=tenacity.retry_if_exception_type(
            exception_types=(APIClientExceptionRetryable,)
        ),
        wait=tenacity.wait_random(min=0, max=1),
        after=my_after,
        reraise=True,
    )
    def wrapped():
        try:
            response = api.post(url=url, json=json, timeout=timeout)
        except (Timeout, ConnectionError) as e:
            raise APIClientExceptionRetryable(
                status_code=-1, detail="A connection error has occured"
            ) from e

        if response.status_code == HTTPStatus.NOT_FOUND:
            # TODO: remove this in taktile-cli 1.0
            raise APISwitchException

        elif response.status_code in DO_NOT_RETRY_STATUS_CODES:
            if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
                raise APIClientException(
                    status_code=response.status_code,
                    detail="An error occurred with your request. Check the deployment's logs for more information",
                )
            elif response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                json_response = response.json()
                raise APIClientException(
                    status_code=response.status_code,
                    detail=f"Unprocessable request body: {json_response['detail']})",
                )
            else:
                json_response = response.json()
                raise APIClientException(
                    status_code=response.status_code,
                    detail=f"Authentication Error: {json_response['detail']}",
                )
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            try:
                json_response = response.json()
                raise APIClientExceptionRetryable(
                    status_code=response.status_code, detail=json_response["detail"],
                ) from e
            except (ValueError, KeyError) as e:
                # Note that we use ValueError instead of JSONDecodeError above on purpose,
                # because depending on runtime configuration `requests` might choose to
                # use `simplejson` which has a different JSONDecodeError. However both derive
                # from ValueError.
                content = response.text
                raise APIClientExceptionRetryable(
                    status_code=response.status_code,
                    detail=f"An error occurred with your request: {content})",
                ) from e
        return response.json()

    return wrapped()


def batch_arrow(
    *, client: FlightClient, action: ActionType, X: t.Any, use_input_index: bool = False
):
    table = serialize_arrow(X)
    batch_size, batch_memory = _get_chunk_size(table)
    if not (batch_size and batch_memory):
        return
    descriptor = client.get_flight_info(FlightDescriptor.for_command(action.type))
    writer, reader = client.do_exchange(descriptor.descriptor)  # type: ignore
    LOG.trace(
        f"Initiating prediction request with batches of {batch_size} records of "
        f"~{batch_memory:.2f} MB/batch"
    )
    batches = table.to_batches(max_chunksize=batch_size)
    chunks = []
    schema = None
    with writer:
        writer.begin(table.schema)
        for i, batch in enumerate(batches):
            LOG.trace(f"Prediction for batch {i + 1}/{len(batches)}")
            chunk = _send_batch(
                writer=writer, batch=batch, reader=reader, batch_number=i + 1
            )
            if not chunk:
                continue
            if not schema and chunk.data.schema is not None:
                schema = chunk.data.schema
            chunks.append(chunk.data)
    deserialized = deserialize_arrow(Table.from_batches(chunks, schema))
    if use_input_index:
        input_has_index = isinstance(X, pd.Series) or isinstance(X, pd.DataFrame)
        output_has_index = isinstance(deserialized, pd.Series) or isinstance(
            deserialized, pd.DataFrame
        )
        if not input_has_index or not output_has_index:
            LOG.warning(
                "Inputs or Outputs are not of type series or dataframe, use_input_index has no effect"
            )
        else:
            try:
                deserialized.index = X.index
            except Exception as e:
                LOG.warning(f"Unable to set indexes of output frame: {repr(e)}")
    return deserialized


def _send_batch(writer, batch, reader, batch_number):
    try:
        writer.write_batch(batch)
        return reader.read_chunk()
    except Exception as e:
        LOG.error(
            f"ERROR: performing prediction for batch {batch_number}: {e} "
            f"The predictions from this batch will be missing from the result"
        )
        return None


def _get_chunk_size(sample_table: Table) -> t.Tuple[t.Optional[int], t.Optional[float]]:
    try:
        mem_per_record = sample_table.nbytes / sample_table.num_rows
    except ZeroDivisionError:
        LOG.error(
            "Empty payload received, which is currently not supported for arrow endpoints"
        )
        return None, None
    batch_size = math.ceil(settings.ARROW_BATCH_MB * 1e6 / mem_per_record)
    batch_memory_mb = (batch_size * mem_per_record) / 1e6
    return batch_size, batch_memory_mb
