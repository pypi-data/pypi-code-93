import time
from typing import Callable, Dict, List, Optional, Union

from requests.models import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.utils._client_config import ClientConfig
from cognite.well_model.wsfe.models import (
    CdfFileLocator,
    CdfFileLocatorItems,
    PatternConfig,
    ProcessIdItems,
    ProcessState,
    ProcessStatus,
)


class WellLogExtractorClient:
    """
    Used to communicate with an instance of the Well Structured File Extractor

    @param api_key (str): API key
    @param project (str): Project
    @param client_name (str): A user-defined name for the client. Used to identify number of unique applications/scripts
            running on top of CDF.
    @param base_url (str): Base url to send requests to.
    @param max_workers (int): Max number of workers to spawn when parallelizing data fetching. Defaults to 10.
    @param headers (Dict): Additional headers to add to all requests.
    @param timeout (int): Timeout on requests sent to the api. Defaults to 60 seconds.
    @param token (Union[str, Callable]): token (Union[str, Callable[[], str]]): A jwt or method which takes no arguments
            and returns a jwt to use for authentication.
    @param token_url (str): Optional url to use for token generation
    @param token_client_id (str): Optional client id to use for token generation.
    @param token_client_secret (str): Optional client secret to use for token generation.
    @param token_scopes (list): Optional list of scopes to use for token generation.
    @param token_custom_args (Dict): Optional additional arguments to use for token generation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project: Optional[str] = None,
        # Unused, but we'll leave it be for consistency with other Cognite clients
        client_name: str = None,
        base_url: Optional[str] = "https://wsfe.cognitedata-development.cognite.ai/v1/greenfield",
        max_workers: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        token: Optional[Union[str, Callable[[], str], None]] = None,
        token_url: Optional[str] = None,
        token_client_id: Optional[str] = None,
        token_client_secret: Optional[str] = None,
        token_scopes: Optional[List[str]] = None,
        token_custom_args: Dict[str, str] = None,
    ):
        self.project = project
        self._config = ClientConfig(
            api_key=api_key,
            project=project,
            client_name=client_name,
            base_url=base_url,
            max_workers=max_workers,
            headers=headers,
            timeout=timeout,
            token=token,
            token_url=token_url,
            token_client_id=token_client_id,
            token_client_secret=token_client_secret,
            token_scopes=token_scopes,
            token_custom_args=token_custom_args,
        )

        self._api_client = APIClient(self._config, cognite_client=self)

    def _path(self, component):
        return f"/{self.project}{component}"

    def submit(self, items: List[CdfFileLocator], write_to_wdl=False, patterns=[]) -> Dict[str, int]:
        """Submit a set of files for extraction"""
        request = CdfFileLocatorItems(
            write_to_wdl=write_to_wdl,
            patterns=PatternConfig(__root__=patterns),
            items=items,
        )

        response: Response = self._api_client.post(self._path("/fromcdf"), json=request.json())
        content: Dict[str, int] = response.json()
        return content

    def submit_chunked(
        self,
        items: List[CdfFileLocator],
        write_to_wdl=False,
        patterns=[],
        chunk_size: int = 100,
        new_chunk_threshold: int = 10,
    ) -> Dict[str, int]:
        """Submits a (assumed large) list of `items` for processing by the WSFE in chunks
        of `chunk_size` each. Will wait with sending the next chunk until the previous chunk is close to done.
        Main purpose: easily submit a large quantity of files for extraction when using JWT tokens for authentication.
        If the `WellLogExtractorClient` is initialized with e.g. a callable to create the JWT token, this will use
        a fresh JWT token for each chunk.
        This reduces the risk of the WSFE not being able to process the item until after the JWT token has expired."""

        def number_of_unfinished(statuses: Dict[int, ProcessState]) -> int:
            return sum(1 for s in statuses.values() if s.status in [ProcessStatus.ready, ProcessStatus.processing])

        content = {}
        for i in range(0, len(items), chunk_size):
            chunk = items[i : i + chunk_size]  # noqa: E203
            # Submit the chunk for processing
            submitted = self.submit(chunk, write_to_wdl=write_to_wdl, patterns=patterns)
            content.update(submitted)
            # Wait for the chunk to be nearly done processing
            self.wait_until(
                list(submitted.values()),
                condition=lambda statuses: number_of_unfinished(statuses) < new_chunk_threshold,
            )

        return content

    def status(self, process_ids: List[int]) -> Dict[int, ProcessState]:
        """Retrieve the status of a set of items previously submitted for extraction"""
        items = ProcessIdItems(items=process_ids)

        response: Response = self._api_client.post(self._path("/status"), json=items.json())
        content: Dict[int, ProcessState] = {k: ProcessState.parse_obj(v) for k, v in response.json().items()}
        return content

    def status_report(self, statuses: List[ProcessState]) -> Dict[str, int]:
        """Partition the set of statuses based on whether they are 'ready', 'processing', 'done' or 'error'"""
        status_types = set(s["status"] for s in statuses)
        return {state: sum(1 for s in statuses if s["status"] == state) for state in status_types}

    def wait_until(
        self,
        process_ids: List[int],
        condition: Callable[[Dict[int, ProcessState]], bool],
        polling_interval: float = 180.0,
    ):
        statuses = self.status(process_ids)
        while not condition(statuses):
            time.sleep(polling_interval)
            statuses = self.status(process_ids)

    def wait(self, process_ids: List[int], polling_interval: float = 180):
        """Waits until all the process ids specified in `process_ids` are either 'done' or 'error'"""
        self.wait_until(
            process_ids,
            condition=lambda statuses: all(
                s.status in [ProcessStatus.error, ProcessStatus.done] for s in statuses.values()
            ),
            polling_interval=polling_interval,
        )
