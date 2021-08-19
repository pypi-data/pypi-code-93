import json
import logging
import os
import subprocess
import sys
import time
import types
import uuid
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from . import __version__
from .db import save_invocation_in_sqlite


logger = logging.getLogger("kolo")
cwd = os.getcwd()


if TYPE_CHECKING:
    from typing import TypedDict

    class ApiRequest(TypedDict):
        method: str
        url: str
        method_and_full_url: str
        body: Optional[str]
        headers: Dict[str, str]
        timestamp: str

    class ApiResponse(TypedDict):
        timestamp: str
        body: str
        status_code: int
        headers: Dict[str, str]

    class ApiInfo(TypedDict, total=False):
        request: ApiRequest
        response: ApiResponse

    class CeleryJob(TypedDict):
        name: str
        args: Tuple[Any, ...]
        kwargs: Dict[str, Any]

    class FrameInfo(TypedDict):
        path: str
        co_name: str
        event: str
        arg: str
        locals: str
        timestamp: float


def _serialize_local(local: object) -> object:
    try:
        json.dumps(local)
    except (TypeError, OverflowError, ValueError):
        try:
            return str(local)
        except Exception:
            return "SerializationError"
    return local


def serialize_frame_locals(frame: types.FrameType) -> str:
    serialized_locals = {
        key: _serialize_local(value) for key, value in frame.f_locals.items()
    }
    return json.dumps(serialized_locals, indent=2)


def serialize_potential_json(arg: object) -> str:
    if arg is None:
        return str(arg)

    try:
        return json.dumps(arg)
    except (TypeError, OverflowError, ValueError):
        return str(arg)


class KoloProfiler:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.timestamp = timezone.now()
        self.invocation_id = f"inv_{uuid.uuid4()}"
        self.frames_of_interest: List[FrameInfo] = []
        self.api_requests_made: List[ApiInfo] = []
        self.jobs_enqueued: List[CeleryJob] = []
        self.request: Optional[Dict[str, Any]] = None
        self.response: Optional[Dict[str, Any]] = None
        self.sql_queries_made: List[Any] = []

    def initialize_request(self, request: HttpRequest):
        self.request = {
            "method": request.method,
            "path_info": request.path_info,
            "body": request.body.decode("utf-8"),
            "headers": {key: value for key, value in request.headers.items()},
        }

    def finalize_response(self, response: HttpResponse) -> None:
        duration = timezone.now() - self.timestamp

        self.response = {
            "ms_duration": round(duration.total_seconds() * 1000, 2),
            "status_code": response.status_code,
            "content": response.content.decode(response.charset),
            "headers": {key: value for key, value in response.items()},
        }
        self.sql_queries_made = connection.queries

    def __call__(self, frame: types.FrameType, event: str, arg: object) -> None:
        if event in ["c_call", "c_return"]:
            return

        filepath = frame.f_code.co_filename
        callable_name = frame.f_code.co_name

        urllib3_request_condition = (
            "urllib3/connectionpool" in filepath and callable_name == "urlopen"
        )
        requests_library_condition = (
            "requests/sessions" in filepath and "request" == callable_name
        )

        celery_condition = (
            "celery" in filepath
            and "apply_async" in callable_name
            and "sentry_sdk" not in filepath
        )

        library_conditions = [
            urllib3_request_condition,
            requests_library_condition,
            celery_condition,
        ]

        if (
            "lib/python" in filepath
            or "lib/pypy" in filepath
            or "/PyPy/" in filepath
            or "/site-packages/" in filepath
        ) and not any(library_conditions):
            # If the virtualenv is stored within the cwd
            # then library calls would be within the cwd.
            # We want to not show library calls, so attempt to
            # filter them out here
            return

        if filepath == "<string>":
            # This frame is running a string executed using exec.
            # We can't show especially interesting information about
            # it, so we skip it.
            return

        if filepath.startswith("<attrs generated"):
            # The attrs library constructs an artificial filename
            # for generated class methods like __init__ and __hash__
            return

        import_modules = (
            "<frozen importlib._bootstrap>",
            "<frozen importlib._bootstrap_external>",
            "<frozen zipimport>",
            "<builtin>/frozen importlib._bootstrap_external",
            "<builtin>/frozen _structseq",
        )
        if filepath in import_modules:
            # This frame is processing an import
            # The import system uses frozen modules, which don't
            # have the same "lib/python" string fragment in their
            # filepath as the standard library or third party code.
            return

        if "/kolo/profiler" in filepath:
            # Don't profile kolo code
            return

        relative_path = frame.f_code.co_filename.replace(f"{cwd}/", "")

        self.frames_of_interest.append(
            {
                "path": f"{relative_path}:{frame.f_lineno}",
                "co_name": callable_name,
                "event": event,
                "arg": serialize_potential_json(arg),
                "locals": serialize_frame_locals(frame),
                "timestamp": time.time(),
            }
        )

        if urllib3_request_condition:
            self.process_api_request_made(frame, event)

        if requests_library_condition:
            self.process_api_response(frame, event)

        if celery_condition:
            self.process_celery_task(frame, event)

    def __enter__(self):
        sys.setprofile(self)

    def __exit__(self, *exc):
        sys.setprofile(None)

    def save_request_in_db(self) -> None:
        current_commit_sha = (
            subprocess.run(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
            .stdout.decode("utf-8")
            .strip()
        )
        json_data = {
            "request_id": self.invocation_id,
            "invocation_id": self.invocation_id,
            "current_commit_sha": current_commit_sha,
            "request": self.request,
            "response": self.response,
            "timestamp": str(self.timestamp),
            "sql_queries_made": self.sql_queries_made,
            "api_requests_made": self.api_requests_made,
            "jobs_enqueued": self.jobs_enqueued,
            "frames_of_interest": self.frames_of_interest,
            "meta": {"version": __version__},
        }

        save_invocation_in_sqlite(
            self.db_path, self.invocation_id, json.dumps(json_data)
        )

    def process_api_request_made(self, frame: types.FrameType, event: str) -> None:
        if event == "return":
            return

        frame_locals = frame.f_locals

        scheme = frame_locals["self"].scheme
        host = frame_locals["self"].host
        url = frame_locals["url"]
        full_url = f"{scheme}://{host}{url}"

        request_headers = frame_locals["headers"]

        request_body = frame_locals["body"]

        if isinstance(request_body, bytes):
            body = request_body.decode("utf-8")
        else:
            body = request_body

        method = frame_locals["method"].upper()
        method_and_full_url = f"{method} {full_url}"

        api_request: ApiInfo = {
            "request": {
                "method": method,
                "url": full_url,
                "method_and_full_url": method_and_full_url,
                "body": body,
                "headers": dict(request_headers),
                "timestamp": timezone.now().isoformat(),
            }
        }

        self.api_requests_made.append(api_request)

    def process_api_response(self, frame: types.FrameType, event: str) -> None:
        if event == "call":
            return

        frame_locals = frame.f_locals

        method = frame_locals["method"].upper()
        url = frame_locals["prep"].url
        method_and_full_url = f"{method} {url}"

        relevant_api_request = None
        negative_target_index = None

        for index, api_request in enumerate(reversed(self.api_requests_made), start=1):
            if method_and_full_url == api_request["request"]["method_and_full_url"]:
                if "response" not in api_request:
                    relevant_api_request = api_request
                    negative_target_index = index

        if relevant_api_request is not None:
            response = frame_locals["resp"]

            relevant_api_request["response"] = {
                "timestamp": timezone.now().isoformat(),
                "body": response.text,
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }

            assert negative_target_index is not None
            self.api_requests_made[-negative_target_index] = relevant_api_request
        else:
            logger.debug(f"No matching request found for {method_and_full_url}")

    def process_celery_task(self, frame: types.FrameType, event: str) -> None:
        if event == "return":
            return

        frame_locals = frame.f_locals
        task_name = frame_locals["self"].name
        task_args = frame_locals["args"]
        task_kwargs = frame_locals["kwargs"]

        job: CeleryJob = {"name": task_name, "args": task_args, "kwargs": task_kwargs}

        self.jobs_enqueued.append(job)
