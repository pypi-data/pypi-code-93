import base64
import datetime
import logging
import threading
from logging import LogRecord
from typing import Any, Dict, List, Optional, cast

import attr
import requests

from .events import Payload
from .failures import FailureContext
from .status import Status
from .types import Headers
from .utils import format_exception


@attr.s(slots=True, repr=False)
class Check:
    """Single check run result."""

    name: str = attr.ib()
    value: Status = attr.ib()
    response: Optional[requests.Response] = attr.ib()
    elapsed: float = attr.ib()
    message: Optional[str] = attr.ib(default=None)
    # Failure-specific context
    context: Optional[FailureContext] = attr.ib(default=None)
    request: Optional[requests.PreparedRequest] = attr.ib(default=None)


@attr.s(slots=True, repr=False)
class Request:
    """Request data extracted from TestCase."""

    method: str = attr.ib()
    uri: str = attr.ib()
    body: Optional[str] = attr.ib()
    headers: Headers = attr.ib()

    @classmethod
    def from_prepared_request(cls, prepared: requests.PreparedRequest) -> "Request":
        """A prepared request version is already stored in `requests.Response`."""
        body = prepared.body

        if isinstance(body, str):
            # can be a string for `application/x-www-form-urlencoded`
            body = body.encode("utf-8")

        # these values have `str` type at this point
        uri = cast(str, prepared.url)
        method = cast(str, prepared.method)
        return cls(
            uri=uri,
            method=method,
            headers={key: [value] for (key, value) in prepared.headers.items()},
            body=base64.b64encode(body).decode() if body is not None else body,
        )


def serialize_payload(payload: bytes) -> str:
    return base64.b64encode(payload).decode()


@attr.s(slots=True, repr=False)
class Response:
    """Unified response data."""

    status_code: int = attr.ib()
    message: str = attr.ib()
    headers: Dict[str, List[str]] = attr.ib()
    body: Optional[str] = attr.ib()
    encoding: Optional[str] = attr.ib()
    http_version: str = attr.ib()
    elapsed: float = attr.ib()

    @classmethod
    def from_requests(cls, response: requests.Response) -> "Response":
        """Create a response from requests.Response."""
        headers = {
            name: response.raw.headers.getlist(name)
            for name in response.raw.headers.keys()
        }
        # Similar to http.client:319 (HTTP version detection in stdlib's `http` package)
        http_version = "1.0" if response.raw.version == 10 else "1.1"

        def is_empty(_response: requests.Response) -> bool:
            # Assume the response is empty if:
            #   - no `Content-Length` header
            #   - no chunks when iterating over its content
            return (
                "Content-Length" not in headers and list(_response.iter_content()) == []
            )

        body = None if is_empty(response) else serialize_payload(response.content)
        return cls(
            status_code=response.status_code,
            message=response.reason,
            body=body,
            encoding=response.encoding,
            headers=headers,
            http_version=http_version,
            elapsed=response.elapsed.total_seconds(),
        )


@attr.s(slots=True)
class Interaction:
    """A single interaction with the target app."""

    request: Request = attr.ib()
    response: Response = attr.ib()
    checks: List[Check] = attr.ib()
    status: Status = attr.ib()
    recorded_at: str = attr.ib(factory=lambda: datetime.datetime.now().isoformat())

    @classmethod
    def from_requests(
        cls, response: requests.Response, status: Status, checks: List[Check]
    ) -> "Interaction":
        return cls(
            request=Request.from_prepared_request(response.request),
            response=Response.from_requests(response),
            status=status,
            checks=checks,
        )


@attr.s(slots=True, repr=False)
class TestResult:
    """Result of a single test."""

    __test__ = False
    checks: List[Check] = attr.ib(factory=list)
    errors: List[Exception] = attr.ib(factory=list)
    interactions: List[Interaction] = attr.ib(factory=list)
    logs: List[LogRecord] = attr.ib(factory=list)
    is_errored: bool = attr.ib(default=False)
    # To show a proper reproduction code if an error happens and there is no way to get actual headers that were
    # sent over the network. Or there could be no actual requests at all
    overridden_headers: Optional[Dict[str, Any]] = attr.ib(default=None)

    def mark_errored(self) -> None:
        self.is_errored = True

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def has_failures(self) -> bool:
        return any(check.value == Status.failure for check in self.checks)

    @property
    def has_logs(self) -> bool:
        return bool(self.logs)

    def add_success(
        self, name: str, response: requests.Response, elapsed: float
    ) -> Check:
        check = Check(
            name=name,
            value=Status.success,
            response=response,
            elapsed=elapsed,
            request=None,
        )
        self.checks.append(check)
        return check

    def add_failure(
        self,
        name: str,
        response: Optional[requests.Response],
        elapsed: float,
        message: str,
        context: Optional[FailureContext],
        request: Optional[requests.PreparedRequest] = None,
    ) -> Check:
        check = Check(
            name=name,
            value=Status.failure,
            response=response,
            elapsed=elapsed,
            message=message,
            context=context,
            request=request,
        )
        self.checks.append(check)
        return check

    def add_error(self, exception: Exception) -> None:
        self.errors.append(exception)

    def store_requests_response(
        self, response: requests.Response, status: Status, checks: List[Check]
    ) -> None:
        self.interactions.append(Interaction.from_requests(response, status, checks))


@attr.s(slots=True)
class SerializedError:
    exception: str = attr.ib()
    exception_with_traceback: str = attr.ib()
    title: Optional[str] = attr.ib()

    @classmethod
    def from_error(
        cls,
        exception: Exception,
        title: Optional[str] = None,
    ) -> "SerializedError":
        return cls(
            exception=format_exception(exception),
            exception_with_traceback=format_exception(exception, True),
            title=title,
        )


@attr.s(slots=True)
class SerializedInteraction:
    request: Request = attr.ib()
    response: Response = attr.ib()
    status: Status = attr.ib()
    recorded_at: str = attr.ib()

    @classmethod
    def from_interaction(cls, interaction: Interaction) -> "SerializedInteraction":
        return cls(
            request=interaction.request,
            response=interaction.response,
            status=interaction.status,
            recorded_at=interaction.recorded_at,
        )


@attr.s(slots=True)
class SerializedTestResult:
    has_failures: bool = attr.ib()
    has_errors: bool = attr.ib()
    has_logs: bool = attr.ib()
    is_errored: bool = attr.ib()
    logs: List[str] = attr.ib()
    errors: List[SerializedError] = attr.ib()
    interactions: List[SerializedInteraction] = attr.ib()

    @classmethod
    def from_test_result(cls, result: TestResult) -> "SerializedTestResult":
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        return cls(
            has_failures=result.has_failures,
            has_errors=result.has_errors,
            has_logs=result.has_logs,
            is_errored=result.is_errored,
            logs=[formatter.format(record) for record in result.logs],
            errors=[SerializedError.from_error(error) for error in result.errors],
            interactions=[
                SerializedInteraction.from_interaction(interaction)
                for interaction in result.interactions
            ],
        )


@attr.s(slots=True)
class InitializedPayload(Payload):
    plan_id: str = attr.ib()
    plan_name: str = attr.ib()
    workspace_id: str = attr.ib()

    # The target URL against which the tests are running
    target_url: str = attr.ib()


@attr.s(slots=True)
class BeforeTestSuiteExecutionPayload(Payload):
    name: str = attr.ib()
    test_suite_id: Optional[str] = attr.ib(default=None)


@attr.s(slots=True)
class AfterTestSuiteExecutionPayload(Payload):
    name: str = attr.ib()
    test_suite_id: Optional[str] = attr.ib(default=None)
    errored: bool = attr.ib(default=False)
    thread_id: int = attr.ib(factory=threading.get_ident)


@attr.s(slots=True)
class BeforeTestExecutionPayload(Payload):
    test_case_id: str = attr.ib()
    name: str = attr.ib()
    method: str = attr.ib()
    path: str = attr.ib()
    relative_path: str = attr.ib()
    test_suite_id: Optional[str] = attr.ib(default=None)
    description: Optional[str] = attr.ib(default=None)

    # The current level of recursion during stateful testing
    recursion_level: int = attr.ib(default=0)


@attr.s(slots=True)
class AfterTestExecutionPayload(Payload):
    test_case_id: str = attr.ib()
    name: str = attr.ib()
    method: str = attr.ib()
    path: str = attr.ib()
    relative_path: str = attr.ib()
    status: Status = attr.ib()
    elapsed_time: float = attr.ib()
    result: Optional[TestResult] = attr.ib()
    test_suite_id: Optional[str] = attr.ib(default=None)
    thread_id: int = attr.ib(factory=threading.get_ident)


@attr.s(slots=True)
class AfterStepExecutionPayload(Payload):
    test_case_id: str = attr.ib()
    name: str = attr.ib()
    sequence: int = attr.ib()
    elapsed_time: float = attr.ib()
    interaction: Interaction = attr.ib()


@attr.s(slots=True)
class FinishedPayload(Payload):
    plan_id: str = attr.ib()
    passed_count: int = attr.ib()
    failed_count: int = attr.ib()
    errored_count: int = attr.ib()

    has_failures: bool = attr.ib(default=False)
    has_errors: bool = attr.ib(default=False)
    generic_errors: List[Exception] = attr.ib(factory=list)
