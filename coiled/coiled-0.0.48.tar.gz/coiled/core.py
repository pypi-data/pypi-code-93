from __future__ import annotations, with_statement

import asyncio
import base64
import contextlib
import copy
import json
import logging
import numbers
import os
import pathlib
import platform
import sys
import threading
import time
import uuid
import warnings
import weakref
from contextlib import contextmanager
from json.decoder import JSONDecodeError
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

import aiohttp
import backoff
import dask
import dask.distributed
import distributed
import rich
import toolz
import yaml
from coiled.exceptions import (
    AWSCredentialsParameterError,
    AzureCredentialsParameterError,
    GCPCredentialsError,
    GCPCredentialsParameterError,
    RegistryParameterError,
    UnsupportedBackendError,
)
from distributed.comm import parse_address
from distributed.utils import Log, Logs, LoopRunner, sync, thread_state
from rich.console import Console
from rich.table import Table
from rich.text import Text
from tornado.ioloop import IOLoop
from typing_extensions import Literal, Protocol

from .compatibility import COILED_VERSION, DISTRIBUTED_VERSION, PY_VERSION
from .context import COILED_SESSION_ID, operation_context, track_context
from .utils import (
    GatewaySecurity,
    Spinner,
    experimental,
    handle_api_exception,
    handle_credentials,
    parse_gcp_region_zone,
    parse_identifier,
    random_str,
    rich_console,
    verify_aws_credentials,
)
from .websockets import (
    ConfigureBackendConnector,
    JobsWebsocketConnector,
    WebsocketConnector,
)

console = Console()


def delete_docstring(func):
    delete_doc = """ Delete a {kind}

Parameters
---------
name
    Name of {kind} to delete.
"""
    func_name = func.__name__
    kind = " ".join(
        func_name.split("_")[1:]
    )  # delete_software_environments -> software environments
    func.__doc__ = delete_doc.format(kind=kind)
    return func


def list_docstring(func):

    list_doc = """ List {kind}s

Parameters
---------
account
    Name of the Coiled account to list {kind}s.
    If not provided, will use the ``coiled.account`` configuration
    value.

Returns
-------
:
    Dictionary with information about each {kind} in the
    specified account. Keys in the dictionary are names of {kind}s,
    while the values contain information about the corresponding {kind}.
"""
    func_name = func.__name__
    kind = " ".join(func_name.split("_")[1:])
    kind = kind[:-1]  # drop trailing "s"
    func.__doc__ = list_doc.format(kind=kind)
    return func


# This lock helps avoid a race condition between cluster creation in the
# in process backend, which temporarily modify coiled's dask config values,
# and the creation of new Cloud objects, with load those same config values.
# This works, but is not ideal.
_cluster_creation_lock = threading.RLock()


# Generic TypeVar for return value from sync/async function.
_T = TypeVar("_T")


# A generic that can only be True/False, allowing us to type async/sync
# versions of coiled objects.
Async = Literal[True]
Sync = Literal[False]
IsAsynchronous = TypeVar("IsAsynchronous", Async, Sync, bool)


# Short of writing type stubs for distributed or typing the underlying package,
# this is a useful cast.
class _SyncProtocol(Protocol):
    def __call__(
        self,
        loop: IOLoop,
        func: Callable[..., Awaitable[_T]],
        *args: Any,
        callback_timeout: numbers.Number,
        **kwargs: Any,
    ) -> _T:
        ...


sync = cast(_SyncProtocol, sync)


class Cloud(Generic[IsAsynchronous]):
    """Connect to Coiled

    Parameters
    ----------
    user
        Username for Coiled account. If not specified, will check the
        ``coiled.user`` configuration value.
    token
        Token for Coiled account. If not specified, will check the
        ``coiled.token`` configuration value.
    server
        Server to connect to. If not specified, will check the
        ``coiled.server`` configuration value.
    account
        The coiled account to use. If not specified,
        will check the ``coiled.account`` configuration value.
    region
        Name of the AWS region to use (e.g. "us-east-2").
        If not specified, will check the ``coiled.aws.region``
        configuration value.
    asynchronous
        Set to True if using this Cloud within ``async``/``await`` functions or
        within Tornado ``gen.coroutines``. Otherwise this should remain
        ``False`` for normal use. Default is ``False``.
    loop
        If given, this event loop will be re-used, otherwise an appropriate one
        will be looked up or created.
    default_cluster_timeout
        Default timeout in seconds to wait for cluster startup before raising ``TimeoutError``.
        Pass ``None`` to wait forever, otherwise the default is 20 minutes.
    """

    _recent_sync: list[weakref.ReferenceType[Cloud[Sync]]] = list()
    _recent_async: list[weakref.ReferenceType[Cloud[Async]]] = list()

    @overload
    def __init__(
        self: Cloud[Sync],
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        region: str = None,
        asynchronous: Sync = False,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        ...

    @overload
    def __init__(
        self: Cloud[Async],
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        region: str = None,
        asynchronous: Async = True,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        ...

    @overload
    def __init__(
        self,
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        region: str = None,
        asynchronous: bool = False,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        ...

    def __init__(
        self,
        user: str = None,
        token: str = None,
        server: str = None,
        account: str = None,
        region: str = None,
        asynchronous: bool = False,
        loop: IOLoop = None,
        default_cluster_timeout: int = 20 * 60,
    ):
        with _cluster_creation_lock:
            self.user = user or dask.config.get("coiled.user")
            self.token = token or dask.config.get("coiled.token")
            self.server = server or dask.config.get("coiled.server")
            if "://" not in self.server:
                self.server = "http://" + self.server
            self.server = self.server.rstrip("/")
            self._default_account = account or dask.config.get("coiled.account")
            self._default_backend_options = (
                dask.config.get("coiled.backend-options", None) or {}
            )
        self.session: Optional[aiohttp.ClientSession] = None
        self.status = "init"
        self.cluster_id: Optional[int] = None
        self._asynchronous = asynchronous
        self._loop_runner = LoopRunner(loop=loop, asynchronous=asynchronous)
        self._loop_runner.start()
        self.default_cluster_timeout = default_cluster_timeout

        if asynchronous:
            Cloud._recent_async.append(weakref.ref(cast(Cloud[Async], self)))
        else:
            Cloud._recent_sync.append(weakref.ref(cast(Cloud[Sync], self)))

        if not self.asynchronous:
            self._sync(self._start)

    def __repr__(self):
        return f"<Cloud: {self.user}@{self.server} - {self.status}>"

    def _repr_html_(self):
        text = (
            '<h3 style="text-align: left;">Cloud</h3>\n'
            '<ul style="text-align: left; list-style: none; margin: 0; padding: 0;">\n'
            f"  <li><b>User: </b>{self.user}</li>\n"
            f"  <li><b>Server: </b>{self.server}</li>\n"
            f"  <li><b>Account: </b>{self.default_account}</li>\n"
        )

        return text

    @property
    def loop(self):
        return self._loop_runner.loop

    @overload
    @classmethod
    def current(cls, asynchronous: Sync) -> Cloud[Sync]:
        ...

    @overload
    @classmethod
    def current(cls, asynchronous: Async) -> Cloud[Async]:
        ...

    @overload
    @classmethod
    def current(cls, asynchronous: bool) -> Cloud:
        ...

    @classmethod
    def current(cls, asynchronous: bool) -> Cloud:
        recent: list[weakref.ReferenceType[Cloud]]
        if asynchronous:
            recent = cls._recent_async
        else:
            recent = cls._recent_sync
        try:
            cloud = recent[-1]()
            while cloud is None or cloud.status != "running":
                recent.pop()
                cloud = recent[-1]()
        except IndexError:
            if asynchronous:
                return Cloud(asynchronous=True)
            else:
                return Cloud(asynchronous=False)
        else:
            return cloud

    @property
    def closed(self) -> bool:
        if self.session:
            return self.session.closed
        # If we haven't opened, we must be closed?
        return True

    @backoff.on_predicate(backoff.expo, lambda resp: resp.status in [502, 503])
    async def _do_request(self, *args, ensure_running: bool = True, **kwargs):
        """
        This wraps the session.request call and injects a per-call UUID.

        Most of the time we check that this is in a "running" state before making
        requests. However, we can disable that by passing in ensure_running=False
        """
        session = self._ensure_session(ensure_running)
        headers = kwargs["headers"] if "headers" in kwargs else {}
        # get frame of caller
        st = sys._getframe(1)
        func = st.f_code.co_name
        # any point in sendin these?
        # path = st.f_code.co_filename
        # lineno = st.f_lineno
        with operation_context("Cloud._do_request") as c_id:
            headers["coiled-operation-id"] = c_id
            headers["coiled-operation-func"] = func
            headers["coiled-request-id"] = random_str()
            kwargs["headers"] = headers
            response = await session.request(*args, **kwargs)
            return response

    def _ensure_session(self, ensure_running=True) -> aiohttp.ClientSession:
        if self.session and (not ensure_running or self.status == "running"):
            return self.session
        else:
            raise RuntimeError("Cloud is not running, did you forget to await it?")

    @track_context
    async def _start(self) -> Cloud:
        if self.status != "init":
            return self
        # Check that server and token are valid
        self.user, self.token, self.server = await handle_credentials(
            server=self.server, token=self.token, save=False
        )
        # TODO: revert when we remove versioneer
        if dask.config.get("coiled.no-minimum-version-check", False):
            client_version = "coiled-frontend-js"
        else:
            client_version = COILED_VERSION

        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": "Token " + self.token,
                "Client-Version": client_version,
                "coiled-session-id": COILED_SESSION_ID,
            }
        )
        # do normal queries
        response = await self._do_request(
            "GET", self.server + "/api/v1/users/me/", ensure_running=False
        )
        if response.status == 426:
            # Upgrade required
            await handle_api_exception(response)
        if response.status >= 400:
            await handle_api_exception(response)

        data = await response.json()
        self.accounts = {
            d["account"]["slug"]: toolz.merge(
                d["account"],
                {"admin": d["is_admin"]},
            )
            for d in data["membership_set"]
        }
        if self._default_account:
            self._verify_account(self._default_account)

        self.status = "running"

        return self

    @property
    def default_account(self):
        if self._default_account:
            return self._default_account
        elif len(self.accounts) == 1:
            return toolz.first(self.accounts)
        elif self.user in self.accounts:
            return self.user
        elif self.user.lower() in self.accounts:
            return self.user.lower()
        else:
            raise ValueError(
                "Please provide an account among the following options",
                list(self.accounts),
            )

    async def _close(self) -> None:
        if self.session:
            await self.session.close()
        self.status = "closed"

    @overload
    def close(self: Cloud[Sync]) -> None:
        ...

    @overload
    def close(self: Cloud[Async]) -> Awaitable[None]:
        ...

    def close(self) -> Optional[Awaitable[None]]:
        """Close connection to Coiled"""
        result = self._sync(self._close)
        self._loop_runner.stop()
        return result

    def __await__(self: Cloud[Async]):
        return self._start().__await__()

    async def __aenter__(self: Cloud[Async]) -> Cloud[Async]:
        return await self._start()

    async def __aexit__(self: Cloud[Async], typ, value, tb) -> None:
        await self._close()

    def __enter__(self: Cloud[Sync]) -> Cloud[Sync]:
        return self

    def __exit__(self: Cloud[Sync], typ, value, tb) -> None:
        self.close()

    @property
    def asynchronous(self) -> bool:
        """Are we running in the event loop?"""
        return self._asynchronous and self.loop is IOLoop.current()

    @overload
    def _sync(
        self: Cloud[Sync],
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: Union[Sync, Literal[None]] = None,
        callback_timeout=None,
        **kwargs,
    ) -> _T:
        ...

    @overload
    def _sync(
        self: Cloud[Async],
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: Union[bool, Literal[None]] = None,
        callback_timeout=None,
        **kwargs,
    ) -> Awaitable[_T]:
        ...

    def _sync(
        self,
        func: Callable[..., Awaitable[_T]],
        *args,
        asynchronous: bool = None,
        callback_timeout=None,
        **kwargs,
    ) -> Union[_T, Awaitable[_T]]:
        callback_timeout = dask.utils.parse_timedelta(callback_timeout, "s")
        if (
            asynchronous
            or self.asynchronous
            or getattr(thread_state, "asynchronous", False)
        ):
            future = func(*args, **kwargs)
            if callback_timeout is not None:
                future = asyncio.wait_for(future, callback_timeout)
            return future
        else:
            return sync(
                self.loop, func, *args, callback_timeout=callback_timeout, **kwargs
            )

    @track_context
    async def _list_clusters(self, account: str = None):
        account = account or self.default_account
        response = await self._do_request(
            "GET", self.server + f"/api/v1/{account}/clusters/"
        )
        if response.status >= 400:
            await handle_api_exception(response)

        data = await response.json()
        return {
            d["name"]: format_cluster_output(d, self.server)
            for d in data["results"]
            if d["status"] in ("pending", "running")
        }

    @overload
    def list_clusters(self: Cloud[Sync], account: str = None) -> dict:
        ...

    @overload
    def list_clusters(self: Cloud[Async], account: str = None) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_clusters(self, account: str = None) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_clusters, account)

    @overload
    def create_cluster(
        self: Cloud[Sync],
        name: str = None,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
    ) -> int:
        ...

    @overload
    def create_cluster(
        self: Cloud[Async],
        name: str = None,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
    ) -> Awaitable[int]:
        ...

    def create_cluster(
        self,
        name: str = None,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
    ) -> Union[int, Awaitable[int]]:
        return self._sync(
            self._create_cluster,
            name=name,
            configuration=configuration,
            software=software,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            account=account,
            workers=workers,
            backend_options=backend_options,
            environ=environ,
        )

    @track_context
    async def _create_cluster(
        self,
        name: str,
        *,
        configuration: str = None,
        software: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        worker_class: str = None,
        worker_options: dict = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        scheduler_class: str = None,
        scheduler_options: dict = None,
        account: str = None,
        workers: int = 0,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
    ) -> int:
        account, name = self._normalize_name(name, context_account=account)
        session = self._ensure_session()
        self._verify_account(account)
        backend_options = {
            **self._default_backend_options,
            **(backend_options or {}),
        }
        environ = environ or {}
        data = {
            "type": "create_cluster",
            "name": name,
            "server": self.server,
            "configuration": configuration,
            "software": software,
            "worker_cpu": worker_cpu,
            "worker_gpu": worker_gpu,
            "worker_memory": max(dask.utils.parse_bytes(worker_memory) // 2 ** 30, 1)
            if worker_memory
            else None,
            "worker_class": worker_class,
            "worker_options": worker_options,
            "scheduler_cpu": scheduler_cpu,
            "scheduler_memory": max(
                dask.utils.parse_bytes(scheduler_memory) // 2 ** 30, 1
            )
            if scheduler_memory
            else None,
            "scheduler_class": scheduler_class,
            "scheduler_options": scheduler_options,
            "workers": workers,
            "options": backend_options,
            "environ": environ,
        }
        ws_server = self.server.replace("http", "ws", 1)

        ws = WebsocketConnector(
            endpoint=f"{ws_server}/ws/api/v1/{account}/clusters/",
            notifications_endpoint=f"{ws_server}/ws/api/v1/{account}/notifications/",
            session=session,
            log_output=log_output,
            connection_error_message=(
                "Unable to connect to server, do you have permissions to "
                f'create clusters in the "{account}" account?'
            ),
        )
        await ws.connect()
        await ws.send_json(data)
        await ws.stream_messages()
        return await self._get_cluster_by_name(name=name, account=account)

    @track_context
    async def _delete_cluster(self, cluster_id: int, account: str = None) -> None:
        account = account or self.default_account
        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/{account}/cluster/{cluster_id}/",
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            rich.print("[green]Cluster deleted successfully.")

    @overload
    def delete_cluster(self: Cloud[Sync], cluster_id: int, account: str = None) -> None:
        ...

    @overload
    def delete_cluster(
        self: Cloud[Async], cluster_id: int, account: str = None
    ) -> Awaitable[None]:
        ...

    @delete_docstring
    def delete_cluster(
        self, cluster_id: int, account: str = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(self._delete_cluster, cluster_id, account)

    @overload
    def get_cluster_by_name(
        self: Cloud[Sync],
        name: str,
        account: str = None,
    ) -> int:
        ...

    @overload
    def get_cluster_by_name(
        self: Cloud[Async],
        name: str,
        account: str = None,
    ) -> Awaitable[int]:
        ...

    def get_cluster_by_name(
        self,
        name: str,
        account: str = None,
    ) -> Union[int, Awaitable[int]]:
        return self._sync(
            self._get_cluster_by_name,
            name=name,
            account=account,
        )

    @track_context
    async def _get_cluster_by_name(self, name: str, account: str = None) -> int:
        """Fetch the latest cluster (pending/running) and store it under cluster_id"""
        account, name = self._normalize_name(name, context_account=account)

        params = {"exclude_statuses": "stopping,stopped"}
        path = self.server + f"/api/v1/{account}/clusters/{name}/"
        response = await self._do_request(
            "GET",
            path,
            params=params,
        )

        if response.status >= 400:
            await handle_api_exception(response)

        cluster = await response.json()
        if cluster["id"] is None:
            raise Exception(f"Could not find cluster '{account}/{name}'")

        self.cluster_id = cast(int, cluster["id"])
        return self.cluster_id

    @track_context
    async def _cluster_status(
        self, cluster_id: int, account: str = None, exclude_stopped: bool = True
    ) -> dict:
        account = account or self.default_account
        params = {}
        if exclude_stopped:
            params = {"exclude_statuses": "stopping,stopped"}
        response = await self._do_request(
            "GET",
            self.server + "/api/v1/{}/cluster/{}/".format(account, cluster_id),
            params=params,
        )
        if response.status >= 400:
            await handle_api_exception(response)
        data = await response.json()
        return data

    @track_context
    async def _security(
        self, cluster_id: int, account: str = None
    ) -> Tuple[dask.distributed.Security, dict]:
        while True:
            data = await self._cluster_status(
                cluster_id=cluster_id, account=account, exclude_stopped=False
            )
            if data["status"] in ["stopped", "stopping"]:
                # cluster is stopped, probably very shortly after starting
                raise ValueError(
                    "Cluster status is unexpectedly STOPPED: it was either unable to start up or died very quickly."
                )
            if data["status"] != "pending" and data["public_address"]:
                break
            else:
                await asyncio.sleep(1.0)
        result = format_security_output(data, cluster_id, self.server)
        security = GatewaySecurity(
            result.get("tls_key"),
            result.get("tls_cert"),
            extra_conn_args=result.get("extra_conn_args"),
        )

        return security, result

    @overload
    def security(
        self: Cloud[Sync], cluster_id: int, account: str = None
    ) -> Tuple[dask.distributed.Security, dict]:
        ...

    @overload
    def security(
        self: Cloud[Async], cluster_id: int, account: str = None
    ) -> Awaitable[Tuple[dask.distributed.Security, dict]]:
        ...

    def security(
        self, cluster_id: int, account: str = None
    ) -> Union[
        Tuple[dask.distributed.Security, dict],
        Awaitable[Tuple[dask.distribued.Security, dict]],
    ]:
        return self._sync(self._security, cluster_id, account)

    @track_context
    async def _scale_up(
        self, cluster_id: int, n: int, account: str = None
    ) -> Optional[Dict]:
        account = account or self.default_account
        response = await self._do_request(
            "PATCH",
            f"{self.server}/api/v1/{account}/cluster/{cluster_id}/scale_up/",
            data={"worker_count_requested": n},
        )
        if response.status >= 400:
            await handle_api_exception(response)

        with contextlib.suppress(aiohttp.ContentTypeError, json.JSONDecodeError):
            result = await response.json()
            if "workers" not in result:
                warning_style = "[bold][yellow]Warning:[/yellow][/bold] "
                try:
                    message = (
                        f"{result['message']}\n"
                        f"code: {result['code']}\n"
                        f"exception: {result['exception']}"
                    )
                    console.print(f"{warning_style} {message}")
                except KeyError:
                    console.print(f"{warning_style} {result}")
                return
            return result

    @overload
    def scale_up(
        self: Cloud[Sync], cluster_id: int, n: int, account: str = None
    ) -> Optional[Dict]:
        ...

    @overload
    def scale_up(
        self: Cloud[Async], cluster_id: int, n: int, account: str = None
    ) -> Awaitable[Optional[Dict]]:
        ...

    def scale_up(
        self, cluster_id: int, n: int, account: str = None
    ) -> Union[Optional[Dict], Awaitable[Optional[Dict]]]:
        """Scale cluster to ``n`` workers

        Parameters
        ----------
        cluster_id
            Unique cluster identifier.
        n
            Number of workers to scale cluster size to.
        account
            Name of Coiled account which the cluster belongs to.
            If not provided, will default to ``Cloud.default_account``.

        """
        return self._sync(self._scale_up, cluster_id, n, account)

    @track_context
    async def _scale_down(
        self, cluster_id: int, workers: Set[str], account: str = None
    ) -> None:
        account = account or self.default_account
        response = await self._do_request(
            "PATCH",
            f"{self.server}/api/v1/{account}/cluster/{cluster_id}/scale_down/",
            data={"del_workers": workers},  # TODO: Hook here
        )
        if response.status >= 400:
            await handle_api_exception(response)

    @overload
    def scale_down(
        self: Cloud[Sync], cluster_id: int, workers: Set[str], account: str = None
    ) -> None:
        ...

    @overload
    def scale_down(
        self: Cloud[Async], cluster_id: int, workers: Set[str], account: str = None
    ) -> Awaitable[None]:
        ...

    def scale_down(
        self, cluster_id: int, workers: Set[str], account: str = None
    ) -> Optional[Awaitable[None]]:
        """Scale cluster to ``n`` workers

        Parameters
        ----------
        cluster_id
            Unique cluster identifier.
        workers
            Set of workers to scale down to.
        account
            Name of Coiled account which the cluster belongs to.
            If not provided, will default to ``Cloud.default_account``.

        """
        return self._sync(self._scale_down, cluster_id, workers, account)

    def _verify_account(self, account: str):
        """Perform sanity checks on account values

        In particular, this raises and informative error message if the
        account is not found, and provides a list of possible options.
        """
        account = account or self.default_account
        if account not in self.accounts:
            raise PermissionError(
                "Account not found: '{}'\n"
                "Possible accounts: {}".format(account, sorted(self.accounts))
            )

    @overload
    def create_software_environment(
        self: Cloud[Sync],
        name: str = None,
        *,
        account: Optional[str] = None,
        conda: Union[list, dict, str] = None,
        pip: Union[list, str] = None,
        container: str = None,
        post_build: Union[list, str] = None,
        conda_env_name: str = None,
        backend_options: Optional[Dict] = None,
        log_output=sys.stdout,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> None:
        ...

    @overload
    def create_software_environment(
        self: Cloud[Async],
        name: str = None,
        *,
        account: Optional[str] = None,
        conda: Union[list, dict, str] = None,
        pip: Union[list, str] = None,
        container: str = None,
        post_build: Union[list, str] = None,
        conda_env_name: str = None,
        backend_options: Optional[Dict] = None,
        log_output=sys.stdout,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> Awaitable[None]:
        ...

    def create_software_environment(
        self,
        name: str = None,
        *,
        account: Optional[str] = None,
        conda: Union[list, dict, str] = None,
        pip: Union[list, str] = None,
        container: str = None,
        post_build: Union[list, str] = None,
        conda_env_name: str = None,
        backend_options: Optional[Dict] = None,
        log_output=sys.stdout,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> Optional[Awaitable[None]]:
        return self._sync(
            self._create_software_environment,
            name=name,
            account=account,
            conda=conda,
            pip=pip,
            container=container,
            post_build=post_build,
            log_output=log_output,
            conda_env_name=conda_env_name,
            backend_options=backend_options,
            private=private,
            force_rebuild=force_rebuild,
            environ=environ,
        )

    @track_context
    async def _create_software_environment(
        self,
        name=None,
        *,
        account: Optional[str] = None,
        conda=None,
        pip=None,
        container=None,
        post_build=None,
        conda_env_name: str = None,
        log_output=sys.stdout,
        backend_options: Optional[Dict] = None,
        private: bool = False,
        force_rebuild: bool = False,
        environ: Optional[Dict] = None,
    ) -> None:
        """
        :param name:
        :param conda:
        :param pip:
        :param container:
        :param post_build:
        :param conda_env_name:
        :param log_output:
        :param backend_options: Dict or None
          backend_options["container_registry"]
        :param private:
        :param force_rebuild:
        :param environ: Dict or None
        :return:
        """
        session = self._ensure_session()
        if conda is None and container is None and pip is not None:
            v = ".".join(map(str, sys.version_info[:2]))
            conda = {"dependencies": [f"python={v}", {"pip": []}]}
        elif isinstance(conda, list):
            conda = {"dependencies": conda}
        elif isinstance(conda, (str, pathlib.Path)):
            # Local conda environment YAML file
            with open(conda, mode="r") as f:
                conda = yaml.safe_load(f)

        if isinstance(pip, (str, pathlib.Path)):
            # Local pip requirements file
            with open(pip, mode="r") as f:
                pip = f.read().splitlines()

        if isinstance(post_build, (str, pathlib.Path)):
            # Post-build script
            with open(post_build, mode="r") as f:
                post_build = f.read().splitlines()

        # Conda supports specifying pip packages via their CLI, but not when
        # using conda.api.Solver. So we move any pip packages to the pip portion
        # of this software environment
        if conda is not None:
            for idx, dep in enumerate(conda["dependencies"]):
                if isinstance(dep, dict) and list(dep.keys()) == ["pip"]:
                    # Copy conda to avoid mutating input from users
                    conda = copy.deepcopy(conda)
                    pip_packages = conda["dependencies"].pop(idx)["pip"]
                    if pip is not None:
                        pip = pip + pip_packages
                    else:
                        pip = pip_packages

        # Remove duplicates and ensure consistent package ordering which helps with
        # downstream tokenization of package spec
        if pip is not None:
            pip = sorted(set(pip))
        if conda is not None:
            conda["dependencies"] = sorted(set(conda["dependencies"]))

        if name is None and conda is not None and "name" in conda:
            name = conda["name"]
        if name is None:
            raise ValueError("Must provide a name when creating a software environment")

        account, name = self._normalize_name(str(name), context_account=account)

        # Connect to the websocket, send the data and get some logs
        data = {
            "type": "build",
            "container": container,
            "conda": conda,
            "conda_env_name": conda_env_name,
            "pip": pip,
            "post_build": post_build,
            "options": {**self._default_backend_options, **(backend_options or {})},
            "private": private,
            "force_rebuild": force_rebuild,
            "environ": environ or {},
        }

        ws_server = self.server.replace("http", "ws", 1)

        ws = WebsocketConnector(
            endpoint=f"{ws_server}/ws/api/v1/{account}/software_environments/{name.lower()}/",
            notifications_endpoint=f"{ws_server}/ws/api/v1/{account}/notifications/",
            session=session,
            log_output=log_output,
            connection_error_message=(
                "Unable to connect to server, do you have permissions to "
                f'create environments in the "{account}" account?'
            ),
        )
        await ws.connect()
        await ws.send_json(data)
        await ws.stream_messages()

    @track_context
    async def _list_software_environments(self, account: Optional[str] = None) -> dict:
        account = account or self.default_account
        response = await self._do_request(
            "GET", self.server + f"/api/v1/{account}/software_environments/"
        )
        if response.status >= 400:
            await handle_api_exception(response)
            return {}
        else:
            results = (await response.json())["results"]

            results = {
                f"{format_account_output(r['account'])}/{r['name']}": format_software_environment_output(
                    r
                )
                for r in results
            }

            return results

    @overload
    def list_software_environments(
        self: Cloud[Sync], account: Optional[str] = None
    ) -> dict:
        ...

    @overload
    def list_software_environments(
        self: Cloud[Async], account: Optional[str] = None
    ) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_software_environments(
        self, account: Optional[str] = None
    ) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_software_environments, account=account)

    def _normalize_name(
        self, name: str, context_account: Optional[str] = None
    ) -> Tuple[str, str]:
        account, name, _ = parse_identifier(name)
        account = account or context_account or self.default_account
        return account, name

    @overload
    def delete_software_environment(
        self: Cloud[Sync], name: str, account: Optional[str] = None
    ) -> None:
        ...

    @overload
    def delete_software_environment(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[None]:
        ...

    @delete_docstring
    def delete_software_environment(
        self, name: str, account: Optional[str] = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(self._delete_software_environment, name, account)

    @track_context
    async def _delete_software_environment(
        self, name: str, account: Optional[str] = None
    ) -> None:
        context_account = account
        account, name, tag = parse_identifier(name)
        account = account or context_account or self.default_account
        if tag:
            name = ":".join([name, tag])
        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/{account}/software_environments/{name}/",
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            rich.print("[green]Software environment deleted successfully.")

    @overload
    def create_cluster_configuration(
        self: Cloud[Sync],
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int = 1,
        worker_gpu: int = 0,
        worker_memory: str = "4 GiB",
        worker_class: str = "dask.distributed.Nanny",
        worker_options: dict = None,
        scheduler_cpu: int = 1,
        scheduler_memory: str = "4 GiB",
        scheduler_class: str = "dask.distributed.Scheduler",
        scheduler_options: dict = None,
        private: bool = False,
    ) -> None:
        ...

    @overload
    def create_cluster_configuration(
        self: Cloud[Async],
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int = 1,
        worker_gpu: int = 0,
        worker_memory: str = "4 GiB",
        worker_class: str = "dask.distributed.Nanny",
        worker_options: dict = None,
        scheduler_cpu: int = 1,
        scheduler_memory: str = "4 GiB",
        scheduler_class: str = "dask.distributed.Scheduler",
        scheduler_options: dict = None,
        private: bool = False,
    ) -> Awaitable[None]:
        ...

    def create_cluster_configuration(
        self,
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int = 1,
        worker_gpu: int = 0,
        worker_memory: str = "4 GiB",
        worker_class: str = "dask.distributed.Nanny",
        worker_options: dict = None,
        scheduler_cpu: int = 1,
        scheduler_memory: str = "4 GiB",
        scheduler_class: str = "dask.distributed.Scheduler",
        scheduler_options: dict = None,
        private: bool = False,
    ) -> Optional[Awaitable[None]]:
        return self._sync(
            self._create_cluster_configuration,
            name=name,
            software=software,
            account=account,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            private=private,
        )

    @track_context
    async def _create_cluster_configuration(
        self,
        name: str,
        software: str,
        *,
        account: Optional[str] = None,
        worker_cpu: int,
        worker_gpu: int,
        worker_memory: str,
        worker_class: str,
        worker_options: dict,
        scheduler_cpu: int,
        scheduler_memory: str,
        scheduler_class: str,
        scheduler_options: dict,
        private: bool,
    ) -> None:
        account, name = self._normalize_name(name, context_account=account)
        data = {
            "software_environment": software,
            "worker_cpu": worker_cpu,
            "worker_gpu": worker_gpu,
            "worker_memory": max(
                # TODO we should be throwing an error instead of choosing
                # 1 if they give use something below 1.
                dask.utils.parse_bytes(worker_memory) // 2 ** 30,
                1,
            ),
            "worker_class": worker_class,
            "worker_options": worker_options or {},
            "scheduler_cpu": scheduler_cpu,
            "scheduler_memory": max(
                dask.utils.parse_bytes(scheduler_memory) // 2 ** 30, 1
            ),
            "scheduler_class": scheduler_class,
            "scheduler_options": scheduler_options or {},
            # TODO environments
            "private": private,
        }
        # Check if we already have a config
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/cluster_configurations/{name}/",
        )
        if response.status == 404:
            rich.print(f"Attempting to create cluster configuration '{name}'...")
            data.update({"name": name})
            response = await self._do_request(
                "POST",
                self.server + f"/api/v1/{account}/cluster_configurations/",
                json=data,
            )
        else:
            rich.print(
                f"Found cluster configuration '{name}', updating this configuration..."
            )
            response = await self._do_request(
                "PATCH",
                self.server + f"/api/v1/{account}/cluster_configurations/{name}/",
                json=data,
            )

        if response.status >= 400:
            await handle_api_exception(response)

    @overload
    def list_cluster_configurations(self: Cloud[Sync], account=None) -> dict:
        ...

    @overload
    def list_cluster_configurations(
        self: Cloud[Async], account=None
    ) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_cluster_configurations(self, account=None) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_cluster_configurations, account=account)

    @track_context
    async def _list_cluster_configurations(self, account=None) -> dict:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/cluster_configurations/",
        )
        if response.status >= 400:
            await handle_api_exception(response)  # will always raise
        results = (await response.json())["results"]
        results = {
            f"{format_account_output(r['account'])}/{r['name']}": format_cluster_configuration_output(
                r
            )
            for r in results
        }
        return results

    @overload
    def list_job_configurations(self: Cloud[Sync], account=None) -> dict:
        ...

    @overload
    def list_job_configurations(self: Cloud[Async], account=None) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_job_configurations(self, account=None) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_job_configurations, account=account)

    @track_context
    async def _list_job_configurations(self, account=None) -> dict:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/process-configurations/",
            params={"only_listable": "True"},
        )
        if response.status >= 400:
            await handle_api_exception(response)  #  will always raise
        results = (await response.json())["results"]
        results = {r["name"]: format_job_configuration_output(r) for r in results}
        return results

    @overload
    def delete_job_configuration(
        self: Cloud[Sync], name: str, account: Optional[str] = None
    ) -> None:
        ...

    @overload
    def delete_job_configuration(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[None]:
        ...

    @delete_docstring
    def delete_job_configuration(
        self, name: str, account: Optional[str] = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(self._delete_job_configuration, name, account)

    @track_context
    async def _delete_job_configuration(
        self, name: str, account: Optional[str] = None
    ) -> None:
        account, name = self._normalize_name(name, context_account=account)
        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/{account}/process-configurations/{name}/",
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            rich.print(f"[green]Deleted '{name}' successfully.")

    @overload
    def list_jobs(self: Cloud[Sync], account: Optional[str] = None) -> dict:
        ...

    @overload
    def list_jobs(self: Cloud[Async], account: Optional[str] = None) -> Awaitable[dict]:
        ...

    @list_docstring
    def list_jobs(self, account: Optional[str] = None) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._list_jobs, account=account)

    @track_context
    async def _list_jobs(self, account: Optional[str] = None) -> dict:
        account = account or self.default_account
        response = await self._do_request(
            "GET", self.server + f"/api/v1/{account}/jobs/"
        )
        if response.status >= 400:
            await handle_api_exception(response)  # will always raise
        results = (await response.json())["results"]
        results = {
            r["name"]: format_job_output(r)
            for r in results
            if r["status"] in ("pending", "running")
        }
        return results

    @overload
    def get_job_by_name(
        self: Cloud[Sync],
        name: str,
        account: str = None,
        backend_options: Optional[Dict] = None,
    ) -> Optional[int]:
        ...

    @overload
    def get_job_by_name(
        self: Cloud[Async],
        name: str,
        account: str = None,
        backend_options: Optional[Dict] = None,
    ) -> Awaitable[Optional[int]]:
        ...

    def get_job_by_name(
        self, name: str, account: str = None, backend_options: Optional[Dict] = None
    ) -> Union[Optional[int], Awaitable[Optional[int]]]:
        return self._sync(
            self._get_job_by_name,
            name=name,
            account=account,
            backend_options=backend_options,
        )

    @track_context
    async def _get_job_by_name(
        self,
        name: str,
        account: str = None,
        backend_options: Optional[Dict] = None,
    ) -> Optional[int]:
        """Fetch the latest running job"""
        account, name = self._normalize_name(name, context_account=account)
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/jobs/{name}/",
            params={"exclude_statuses": "pending,stopped"},
        )

        if response.status >= 400:
            await handle_api_exception(response)

        job = await response.json()
        return job["id"]

    @overload
    def delete_cluster_configuration(
        self: Cloud[Sync], name: str, account: Optional[str] = None
    ) -> None:
        ...

    @overload
    def delete_cluster_configuration(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[None]:
        ...

    @delete_docstring
    def delete_cluster_configuration(
        self, name: str, account: Optional[str] = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(self._delete_cluster_configuration, name, account)

    @track_context
    async def _delete_cluster_configuration(
        self, name: str, account: Optional[str] = None
    ):
        account, name = self._normalize_name(name, context_account=account)

        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/{account}/cluster_configurations/{name}/",
        )
        if response.status >= 400:
            await handle_api_exception(response)
        else:
            rich.print("[green]Cluster configuration deleted successfully.")

    @overload
    def create_job_configuration(
        self: Cloud[Sync],
        name: str,
        command: List[str],
        software: str,
        *,
        account: Optional[str] = None,
        cpu: int = 1,
        gpu: int = 0,
        memory: str = "4 GiB",
        ports: List = None,
        files: Union[str, List[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        ...

    @overload
    def create_job_configuration(
        self: Cloud[Async],
        name: str,
        command: List[str],
        software: str,
        *,
        account: Optional[str] = None,
        cpu: int = 1,
        gpu: int = 0,
        memory: str = "4 GiB",
        ports: List = None,
        files: Union[str, List[str]] = None,
        description: Optional[str] = None,
    ) -> Awaitable[None]:
        ...

    def create_job_configuration(
        self,
        name: str,
        command: List[str],
        software: str,
        *,
        account: Optional[str] = None,
        cpu: int = 1,
        gpu: int = 0,
        memory: str = "4 GiB",
        ports: List = None,
        files: Union[str, List[str]] = None,
        description: Optional[str] = None,
    ) -> Optional[Awaitable[None]]:
        return self._sync(
            self._create_job_configuration,
            name=name,
            command=command,
            software=software,
            account=account,
            cpu=cpu,
            gpu=gpu,
            memory=memory,
            ports=ports,
            files=files,
            description=description,
        )

    @track_context
    async def _create_job_configuration(
        self,
        name: str,
        command: List[str],
        software: str,
        *,
        account: Optional[str] = None,
        cpu: int = 1,
        gpu: int = 0,
        memory: str = "4 GiB",
        ports: List = None,
        files: Union[str, List[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        account, name = self._normalize_name(name, context_account=account)

        if isinstance(files, str):
            files = [files]

        file_mapping = {}
        if files is not None:
            for path in files:
                with open(path, "rb") as f:
                    file_mapping[os.path.basename(path)] = base64.b64encode(
                        f.read()
                    ).decode("utf8")

        data = {
            "software_environment": software,
            "cpu": cpu,
            "gpu": gpu,
            "memory": max(
                # TODO we should be throwing an error instead of choosing
                # 1 if they give use something below 1.
                dask.utils.parse_bytes(memory) // 2 ** 30,
                1,
            ),
            "command": command,
            "ports": ports or [],
            "listable": True,
            "files": file_mapping,
            "description": description,
            # TODO environments
        }
        # Check if we already have a config
        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/process-configurations/{name}/",
        )
        if response.status == 404:
            data.update({"name": name})
            response = await self._do_request(
                "POST",
                self.server + f"/api/v1/{account}/process-configurations/",
                json=data,
            )
        else:
            response = await self._do_request(
                "PATCH",
                self.server + f"/api/v1/{account}/process-configurations/{name}/",
                json=data,
            )

        if response.status >= 400:
            await handle_api_exception(response)

    @overload
    def start_job(
        self: Cloud[Sync],
        configuration: str = None,
        account: str = None,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        log_output=sys.stdout,
    ) -> str:
        ...

    @overload
    def start_job(
        self: Cloud[Async],
        configuration: str = None,
        account: str = None,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        log_output=sys.stdout,
    ) -> Awaitable[str]:
        ...

    def start_job(
        self,
        configuration: str = None,
        account: str = None,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        log_output=sys.stdout,
    ) -> Union[str, Awaitable[str]]:

        return self._sync(
            self._start_job,
            configuration=configuration,
            account=account,
            backend_options=backend_options,
            environ=environ,
            log_output=log_output,
        )

    @track_context
    async def _start_job(
        self,
        configuration: str,
        account: str = None,
        backend_options: Optional[Dict] = None,
        environ: Optional[Dict] = None,
        log_output=sys.stdout,
    ) -> str:
        account, name = self._normalize_name(configuration, context_account=account)
        session = self._ensure_session()
        self._verify_account(account)
        name = self.user + "-" + name + "-" + str(uuid.uuid4())[:10]
        logging_context = {}
        data = {
            "name": name,
            "logging_context": logging_context,
            # TODO why do we need to send the server's url
            # to itself?
            "server": self.server,
            "job": configuration,
            "options": {**self._default_backend_options, **(backend_options or {})},
            "environ": environ or {},
        }
        ws_server = self.server.replace("http", "ws", 1)
        ws = JobsWebsocketConnector(
            endpoint=f"{ws_server}/ws/api/v1/{account}/jobs/",
            notifications_endpoint=f"{ws_server}/ws/api/v1/{account}/notifications/",
            session=session,
            log_output=log_output,
            connection_error_message=(
                "Unable to connect to server, do you have permissions to "
                f'start jobs in the "{account}" account?'
            ),
        )
        await ws.connect()
        await ws.send_json(data)
        print("Starting job. This might take a few minutes ...", end="")
        with Spinner():
            await ws.stream_messages()

        return name

    @overload
    def set_backend_options(
        self: Cloud[Sync],
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> str:
        ...

    @overload
    def set_backend_options(
        self: Cloud[Async],
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> Awaitable[str]:
        ...

    def set_backend_options(
        self,
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> Union[str, Awaitable[str]]:

        return self._sync(
            self._set_backend_options,
            backend_options,
            account=account,
            log_output=log_output,
        )

    @track_context
    async def _set_backend_options(
        self,
        backend_options: dict,
        account: str = None,
        log_output=sys.stdout,
    ) -> str:
        session = self._ensure_session()
        account = account or self.default_account
        self._verify_account(account)
        logging_context = {}
        default_configuration_message = {
            "type": "update_options",
            "logging_context": logging_context,
            "data": backend_options,
        }

        ws_server = self.server.replace("http", "ws", 1)
        ws = ConfigureBackendConnector(
            endpoint=f"{ws_server}/ws/api/v1/{account}/cluster-info/",
            notifications_endpoint=f"{ws_server}/ws/api/v1/{account}/notifications/",
            session=session,
            log_output=log_output,
            connection_error_message=(
                "Unable to connect to server, do you have permissions to "
                f'edit backend_options in the "{account}" account?'
            ),
        )
        await ws.connect()
        await ws.send_json(default_configuration_message)
        with Spinner():
            await ws.stream_messages()
        return f"{self.server}/{account}/account"

    @overload
    def stop_job(self: Cloud[Sync], name: str, account: Optional[str] = None) -> None:
        ...

    @overload
    def stop_job(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[None]:
        ...

    def stop_job(
        self, name: str, account: Optional[str] = None
    ) -> Optional[Awaitable[None]]:
        return self._sync(
            self._stop_job,
            name=name,
            account=account,
        )

    @track_context
    async def _stop_job(self, name: str, account: Optional[str] = None) -> None:
        account = account or self.default_account
        response = await self._do_request(
            "DELETE",
            self.server + f"/api/v1/{account}/jobs/{name}/",
        )
        if response.status >= 400:
            await handle_api_exception(response)

    @overload
    def cluster_logs(
        self: Cloud[Sync],
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Logs:
        ...

    @overload
    def cluster_logs(
        self: Cloud[Async],
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Awaitable[Logs]:
        ...

    def cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Union[Logs, Awaitable[Logs]]:
        return self._sync(self._cluster_logs, cluster_id, account, scheduler, workers)

    @track_context
    async def _cluster_logs(
        self,
        cluster_id: int,
        account: str = None,
        scheduler: bool = True,
        workers: bool = True,
    ) -> Logs:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + "/api/v1/{}/cluster/{}/logs/".format(account, cluster_id),
        )
        if response.status >= 400:
            await handle_api_exception(response)

        data = await response.json()
        # munge the response to match the signature of Cluster's parent class
        out = {}
        if scheduler:
            out["Scheduler"] = Log(data["scheduler"]["logs"])
        if workers:
            for w in data["workers"]:
                out[w["name"]] = Log(w["logs"])

        return Logs(out)

    @overload
    def job_logs(
        self: Cloud[Sync],
        job_id: int,
        account: str = None,
    ) -> Logs:
        ...

    @overload
    def job_logs(
        self: Cloud[Async],
        job_id: int,
        account: str = None,
    ) -> Awaitable[Logs]:
        ...

    def job_logs(
        self,
        job_id: int,
        account: str = None,
    ) -> Union[Logs, Awaitable[Logs]]:
        return self._sync(self._job_logs, job_id, account=account)

    @track_context
    async def _job_logs(
        self,
        job_id: int,
        account: str = None,
    ) -> Logs:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            self.server + "/api/v1/{}/jobs/{}/logs/".format(account, job_id),
        )
        if response.status >= 400:
            await handle_api_exception(response)

        data = await response.json()

        return Logs({"Process": Log(data["process"]["logs"])})

    @track_context
    async def get_aws_credentials(self, account: str = None):
        """Return the logged in user's AWS credentials"""
        account = account or self.default_account
        response = await self._do_request(
            "GET", self.server + f"/api/v1/{account}/backend_options/"
        )
        if response.status >= 400:
            await handle_api_exception(response)

        backend_options = await response.json()
        if backend_options["backend"] != "ecs":
            return {}

        credentials = backend_options.get("options", {}).get("credentials", {})
        return credentials

    @overload
    def get_software_info(
        self: Cloud[Sync], name: str, account: Optional[str] = None
    ) -> dict:
        ...

    @overload
    def get_software_info(
        self: Cloud[Async], name: str, account: Optional[str] = None
    ) -> Awaitable[dict]:
        ...

    def get_software_info(
        self, name: str, account: Optional[str] = None
    ) -> Union[dict, Awaitable[dict]]:
        return self._sync(self._get_software_info, name=name, account=account)

    @track_context
    async def _get_software_info(
        self, name: str, account: Optional[str] = None
    ) -> dict:
        """Retrieve solved spec for a Coiled software environment

        Parameters
        ----------
        name
            Software environment name

        Returns
        -------
        results
            Coiled software environment information
        """
        account, name = self._normalize_name(name, context_account=account)

        response = await self._do_request(
            "GET",
            self.server + f"/api/v1/{account}/software_environments/{name}/",
        )
        if response.status >= 400:
            text = await response.text()
            if "Not found" in text:
                raise ValueError(
                    f"Could not find a '{account}/{name}' Coiled software environment"
                )
            else:
                await handle_api_exception(response)

        results = await response.json()
        return results

    @overload
    def cluster_cost_estimate(
        self: Cloud[Sync],
        *,
        account: str = None,
        n_workers: int = 4,
        configuration: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        backend_options: Optional[Dict] = None,
    ) -> str:
        ...

    @overload
    def cluster_cost_estimate(
        self: Cloud[Async],
        *,
        account: str = None,
        n_workers: int = 4,
        configuration: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        backend_options: Optional[Dict] = None,
    ) -> Awaitable[str]:
        ...

    def cluster_cost_estimate(
        self,
        *,
        account: str = None,
        n_workers: int = 4,
        configuration: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        backend_options: Optional[Dict] = None,
    ) -> Union[str, Awaitable[str]]:
        return self._sync(
            self._cluster_cost_estimate,
            account=account,
            n_workers=n_workers,
            configuration=configuration,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            backend_options=backend_options,
        )

    @track_context
    async def _cluster_cost_estimate(
        self,
        *,
        account: str = None,
        n_workers: int = None,
        configuration: str = None,
        worker_cpu: int = None,
        worker_gpu: int = None,
        worker_memory: Union[str, int] = None,
        scheduler_cpu: int = None,
        scheduler_memory: Union[str, int] = None,
        backend_options: Optional[Dict] = None,
    ) -> str:
        account = account or self.default_account
        response = await self._do_request(
            "POST",
            self.server + f"/api/v1/{account}/cluster/cost-estimate/",
            json={
                "n_workers": n_workers,
                "configuration": configuration,
                "worker_cpu": worker_cpu,
                "worker_memory": max(
                    dask.utils.parse_bytes(worker_memory) // 2 ** 30, 1
                )
                if worker_memory
                else None,
                "worker_gpu": worker_gpu,
                "scheduler_cpu": scheduler_cpu,
                "scheduler_memory": max(
                    dask.utils.parse_bytes(scheduler_memory) // 2 ** 30, 1
                )
                if scheduler_memory
                else None,
                "options": {**self._default_backend_options, **(backend_options or {})},
            },
        )

        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        return f"${result['cost']}/hr"

    @overload
    def list_core_usage(
        self: Cloud[Sync], json: Literal[False], account: str = None
    ) -> None:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Async], json: Literal[False], account: str = None
    ) -> Awaitable[None]:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Sync], json: Literal[True], account: str = None
    ) -> dict:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Async], json: Literal[True], account: str = None
    ) -> Awaitable[dict]:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Async], json: bool, account: str = None
    ) -> Awaitable[Optional[dict]]:
        ...

    @overload
    def list_core_usage(
        self: Cloud[Sync], json: bool, account: str = None
    ) -> Optional[dict]:
        ...

    def list_core_usage(
        self, json: bool = False, account: str = None
    ) -> Union[Awaitable[Optional[dict]], Optional[dict]]:
        return self._sync(self._list_core_usage, json=json, account=account)

    @track_context
    async def _list_core_usage(
        self, json: bool = False, account: str = None
    ) -> Optional[dict]:
        account = account or self.default_account

        response = await self._do_request(
            "GET", f"{self.server}/api/v1/{account}/usage/cores/"
        )

        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()

        if json:
            return result

        cores_table = Table(title="Core usage")
        cores_table.add_column("Tier Limit", justify="center")
        cores_table.add_column("User Core Limit", justify="center")
        cores_table.add_column("User Total", justify="center")
        cores_table.add_column("Account Total", justify="center")
        cores_table.add_column("Cores used by Clusters", justify="center")
        cores_table.add_column("Cores used by Jobs", justify="center")
        cores_table.add_column("Credits Total", justify="center")
        cores_table.add_column("Credits Used", justify="center")

        cores_table.add_row(
            str(result["tier_limit"]),
            str(result["core_limit"]),
            str(result["user_total"]),
            str(result["account_total"]),
            str(result["clusters_total"]),
            str(result["jobs_total"]),
            str(result["quota"]),
            str(result["spent"]),
        )

        console = Console()
        console.print(cores_table)
        return None

    async def _list_local_versions(self, json: bool = False) -> Union[dict, None]:
        versions_table = Table(title="Versions")
        versions_table.add_column("Operating System", justify="center")
        versions_table.add_column("Python Version", justify="center")
        versions_table.add_column("Pip Version", justify="center"),
        versions_table.add_column("Conda Version", justify="center")
        versions_table.add_column("Coiled Version", justify="center")
        versions_table.add_column("Dask Version", justify="center")
        versions_table.add_column("Distributed Version", justify="center")

        try:
            import conda

            conda_version = conda.__version__
        except ModuleNotFoundError:
            conda_version = "None"

        try:
            import pip

            pip_version = pip.__version__
        except ModuleNotFoundError:
            pip_version = "None"

        versions_table.add_row(
            platform.platform(),
            str(PY_VERSION),
            pip_version,
            conda_version,
            str(COILED_VERSION),
            dask.__version__,
            distributed.__version__,
        )

        if json:
            return {
                "operating_system": platform.platform(),
                "python_version": PY_VERSION,
                "pip_version": pip_version,
                "conda_version": conda_version,
                "coiled_version": COILED_VERSION,
                "dask_version": dask.__version__,
                "distributed_version": distributed.__version__,
            }

        console.print(versions_table)
        return None

    @overload
    def list_local_versions(self: Cloud[Sync], json: Literal[False]) -> None:
        ...

    @overload
    def list_local_versions(
        self: Cloud[Async], json: Literal[False]
    ) -> Awaitable[None]:
        ...

    @overload
    def list_local_versions(self: Cloud[Sync], json: Literal[True]) -> dict:
        ...

    @overload
    def list_local_versions(self: Cloud[Async], json: Literal[True]) -> Awaitable[dict]:
        ...

    @overload
    def list_local_versions(self: Cloud[Sync], json: bool) -> Optional[dict]:
        ...

    @overload
    def list_local_versions(
        self: Cloud[Async], json: bool
    ) -> Awaitable[Optional[dict]]:
        ...

    def list_local_versions(
        self, json: bool = False
    ) -> Union[Awaitable[Optional[dict]], Optional[dict]]:
        return self._sync(self._list_local_versions, json=json)

    @overload
    def get_notifications(
        self: Cloud[Sync],
        json: Literal[True],
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> List[dict]:
        ...

    @overload
    def get_notifications(
        self: Cloud[Async],
        json: Literal[True],
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Awaitable[List[dict]]:
        ...

    @overload
    def get_notifications(
        self: Cloud[Sync],
        json: bool,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Optional[List[dict]]:
        ...

    @overload
    def get_notifications(
        self: Cloud[Async],
        json: bool,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Awaitable[Optional[List[dict]]]:
        ...

    def get_notifications(
        self,
        json: bool = False,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Union[Awaitable[Optional[List[dict]]], Optional[List[dict]]]:
        return self._sync(
            self._get_notifications,
            json=json,
            account=account,
            limit=limit,
            level=level,
        )

    @track_context
    async def _get_notifications(
        self,
        json: bool = False,
        account: str = None,
        limit: int = 100,
        level: Union[int, str] = logging.NOTSET,
    ) -> Optional[List[dict]]:
        account = account or self.default_account

        response = await self._do_request(
            "GET",
            f"{self.server}/api/v1/{account}/notifications/",
            params={"limit": limit, "level": level},
        )

        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        notifications: List[dict] = result["notifications"]

        if json:
            return notifications

        notifications_table = Table(title="Notifications")
        notifications_table.add_column("time", justify="center", overflow="fold")
        notifications_table.add_column("id", justify="center", overflow="fold")
        notifications_table.add_column("level", justify="center", overflow="fold")
        notifications_table.add_column("event_type", justify="center", overflow="fold")
        notifications_table.add_column("msg", justify="center", overflow="fold")
        notifications_table.add_column("data", justify="center", overflow="fold")

        for notification in notifications:
            try:
                local_time = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(notification["timestamp"])
                )
            except KeyError:
                local_time = "???"
            notifications_table.add_row(
                str(local_time),
                str(notification.get("id", "")),
                logging.getLevelName(notification.get("level", "")),
                str(notification.get("event_type", "")),
                str(notification["msg"]),
                str(notification.get("data", "")),
            )

        console = Console()
        console.print(notifications_table)
        return None

    @track_context
    async def _noop_wait(self, duration: int):
        response = await self._do_request(
            "GET", self.server + f"/api/v1/_noop_wait/{int(duration)}"
        )

        result = await response.json()
        return result

    @track_context
    async def _upload_performance_report(
        self,
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Dict:
        account = account or self.default_account

        data = aiohttp.MultipartWriter("form-data")
        part = data.append(open(content, "rb"))
        part.headers[
            aiohttp.hdrs.CONTENT_DISPOSITION
        ] = f'form-data; name="file"; filename="{filename}"; filename*="{filename}"'

        upload_type = "private" if private else "public"
        response = await self._do_request(
            "POST",
            f"{self.server}/api/v1/{account}/performance_reports/{upload_type}/",
            data=data,
        )

        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        return result

    @overload
    def upload_performance_report(
        self: Cloud[Sync],
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Dict:
        ...

    @overload
    def upload_performance_report(
        self: Cloud[Async],
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Awaitable[Dict]:
        ...

    def upload_performance_report(
        self,
        content: str,
        account: str = None,
        filename: str = None,
        private: bool = False,
    ) -> Union[Dict, Awaitable[Dict]]:
        return self._sync(
            self._upload_performance_report,
            content,
            filename=filename,
            account=account,
            private=private,
        )

    @track_context
    async def _list_performance_reports(
        self,
        account: str = None,
    ) -> List[Dict]:
        account = account or self.default_account
        response = await self._do_request(
            "GET",
            f"{self.server}/api/v1/{account}/performance_reports/all/",
        )
        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        return result

    @overload
    def list_performance_reports(
        self: Cloud[Async],
        account: str = None,
    ) -> Awaitable[List[Dict]]:
        ...

    @overload
    def list_performance_reports(
        self: Cloud[Sync],
        account: str = None,
    ) -> List[Dict]:
        ...

    def list_performance_reports(
        self,
        account: str = None,
    ) -> Union[List[Dict], Awaitable[List[Dict]]]:
        return self._sync(
            self._list_performance_reports,
            account=account,
        )

    @overload
    def list_user_information(self: Cloud[Sync]) -> dict:
        ...

    @overload
    def list_user_information(self: Cloud[Async]) -> Awaitable[dict]:
        ...

    def list_user_information(self) -> Union[Awaitable[dict], dict]:
        return self._sync(self._list_user_information)

    @track_context
    async def _list_user_information(
        self,
    ) -> dict:
        response = await self._do_request("GET", self.server + "/api/v1/users/me/")
        if response.status >= 400:
            await handle_api_exception(response)
        result = await response.json()

        return result

    @track_context
    async def _health_check(self) -> dict:
        response = await self._do_request("GET", self.server + "/api/v1/health")
        if response.status >= 400:
            await handle_api_exception(response)

        result = await response.json()
        return result

    @overload
    def health_check(self: Cloud[Sync]) -> dict:
        ...

    @overload
    def health_check(self: Cloud[Async]) -> Awaitable[dict]:
        ...

    def health_check(self) -> Union[Awaitable[dict], dict]:
        return self._sync(self._health_check)


# Utility functions for formatting list_* endpoint responses to be more user-friendly


def format_security_output(data, cluster_id, server):
    d = data.copy()
    scheme, _ = parse_address(d["public_address"])
    if scheme.startswith("ws"):
        address = f"{server.replace('http', 'ws')}/cluster/{cluster_id}/"
        d["public_address"] = address
        d["dashboard_address"] = f"{server}/dashboard/{cluster_id}/status"
        d.pop("tls_key")
        d.pop("tls_cert")
    else:
        d.pop("extra_conn_args")
    return d


def format_account_output(d):
    return d["slug"]


def format_software_environment_output(d):
    exclude_list = [
        "id",
        "name",
        "content_hash",
        "builds",
    ]
    d = {k: v for k, v in d.items() if k not in exclude_list}
    d["account"] = format_account_output(d["account"])
    return d


def format_cluster_configuration_output(d):
    d = d.copy()
    d.pop("id")
    d.pop("name")
    d["account"] = format_account_output(d["account"])
    for process in ["scheduler", "worker"]:
        d[process].pop("id")
        d[process].pop("name")
        d[process].pop("account")
        d[process]["software"] = d[process]["software_environment"]
        d[process].pop("software_environment")
    return d


def format_cluster_output(d, server):
    d = d.copy()
    for key in ["auth_token", "private_address", "name", "last_seen"]:
        d.pop(key)
    d["account"] = format_account_output(d["account"])
    # Rename "public_address" to "address"
    address = d.pop("public_address")
    scheme, _ = parse_address(address)
    if scheme.startswith("ws"):
        address = f"{server.replace('http', 'ws')}/cluster/{d['id']}/"
    d["address"] = address
    # Use proxied dashboard address if we're in a hosted notebook
    # or proxying through websockets
    if dask.config.get("coiled.dashboard.proxy", False) or scheme.startswith("ws"):
        d["dashboard_address"] = f"{server}/dashboard/{d['id']}/status"
    return d


def format_job_configuration_output(d):
    d = d.copy()
    d["software"] = d["software_environment"]
    # d["software"] = "/".join(
    #     [
    #         d["software_environment"]["account"]["slug"],
    #         d["software_environment"]["name"],
    #     ]
    # )
    if d["files"] is not None:
        d["files"] = list(d["files"].keys())
    for key in ["id", "software_environment", "name", "listable"]:
        d.pop(key)

    d["account"] = format_account_output(d["account"])

    return d


def format_job_output(d):
    d = d.copy()
    d["configuration"] = "/".join(
        [d["process"]["account"]["slug"], d["process"]["name"]]
    )
    for key in ["process", "name"]:
        d.pop(key)

    d["account"] = format_account_output(d["account"])

    return d


# Public API


def create_software_environment(
    name: str = None,
    *,
    account: Optional[str] = None,
    conda: Union[list, dict, str] = None,
    pip: Union[list, str] = None,
    container: str = None,
    log_output=sys.stdout,
    post_build: Union[list, str] = None,
    conda_env_name: str = None,
    backend_options: Optional[Dict] = None,
    private: bool = False,
    force_rebuild: bool = False,
    environ: Optional[Dict] = None,
) -> None:
    """Create a software environment

    Parameters
    ---------
    name
        Name of software environment. Name can't contain uppercase letters.
    account
        The account in which to create the software environment, if not given in the name.
    conda
        Specification for packages to install into the software environment using conda.
        Can be a list of packages, a dictionary, or a path to a conda environment YAML file.
    pip
        Packages to install into the software environment using pip.
        Can be a list of packages or a path to a pip requirements file.
    container
        Docker image to use for the software environment. Must be the name of a docker image
        on Docker hub. Defaults to ``coiled/default``.
    post_build
        List of commands or path to a local executable script to run after pip and conda packages
        have been installed.
    log_output
        Stream to output logs to. Defaults to ``sys.stdout``.
    conda_env_name
        Name of conda environment to install packages into. Note that this should *only* be used
        when specifying a non-default value for ``container`` *and* when the non-default Docker
        image used expects commands to run in a conda environment not named "coiled".
        Defaults to "coiled".
    backend_options
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``). Any options
        specified with this keyword argument will take precedence over those stored in the
        ``coiled.backend-options`` configuration value.
    private
        Whether this software environment is private or public. Defaults to ``False``
    force_rebuild
        By default, if an existing software environment with the same name and dependencies already
        exists, a rebuild is aborted. If this is set to True, those checks are skipped and the
        environment will be rebuilt. Defaults to ``False``
    environ
        Dictionary of environment variables.
    """
    with Cloud() as cloud:
        return cloud.create_software_environment(
            name=name,
            account=account,
            conda=conda,
            pip=pip,
            container=container,
            post_build=post_build,
            log_output=log_output,
            conda_env_name=conda_env_name,
            backend_options=backend_options,
            private=private,
            force_rebuild=force_rebuild,
            environ=environ,
        )


@list_docstring
def list_software_environments(account=None):
    with Cloud(account=account) as cloud:
        return cloud.list_software_environments(account=account)


@delete_docstring
def delete_software_environment(name):
    with Cloud() as cloud:
        return cloud.delete_software_environment(name=name)


def get_software_info(name: str, account: Optional[str] = None) -> dict:
    """Retrieve solved spec for a Coiled software environment

    Parameters
    ----------
    name
        Software environment name

    Returns
    -------
    results
        Coiled software environment information
    """
    with Cloud() as cloud:
        return cloud.get_software_info(name=name, account=account)


def create_cluster_configuration(
    name: str,
    software: str,
    *,
    account: str = None,
    worker_cpu: int = 1,
    worker_gpu: int = 0,
    worker_memory: str = "4 GiB",
    worker_class: str = "dask.distributed.Nanny",
    worker_options: dict = None,
    scheduler_cpu: int = 1,
    scheduler_memory: str = "4 GiB",
    scheduler_class: str = "dask.distributed.Scheduler",
    scheduler_options: dict = None,
    private: bool = False,
) -> None:
    """Create a cluster configuration

    Parameters
    ----------
    name
        Name of cluster configuration.
        Optionally prefixed with an account name like "myaccount/myname"
    software
        Identifier of the software environment to use, in the format (<account>/)<name>. If the software environment
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.

        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have an environment
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".

        The "name" portion of (<account>/)<name> can only contain ASCII letters, hyphens and underscores.
    account
        The account in which to create the cluster configuration, if not given in the name.
    worker_cpu
        Number of CPUs allocated for each worker. Defaults to 1.
    worker_gpu
        Number of GPUs allocated for each worker. Defaults to 0 (no GPU support). Note that this will _always_
        allocate GPU-enabled workers, so is expensive.
    worker_memory
        Amount of memory to allocate for each worker. Defaults to 4 GiB.
    worker_class
        Worker class to use. Defaults to "dask.distributed.Nanny".
    worker_options
        Mapping with keyword arguments to pass to ``worker_class``. Defaults to ``{}``.
    scheduler_cpu
        Number of CPUs allocated for the scheduler. Defaults to 1.
    scheduler_memory
        Amount of memory to allocate for the scheduler. Defaults to 4 GiB.
    scheduler_class
        Scheduler class to use. Defaults to "dask.distributed.Scheduler".
    scheduler_options
        Mapping with keyword arguments to pass to ``scheduler_class``. Defaults to ``{}``.
    private
        Whether this cluster configuration is private or public. Defaults to ``False``

    See Also
    --------
    dask.utils.parse_bytes
    """
    with Cloud() as cloud:
        return cloud.create_cluster_configuration(
            name=name,
            software=software,
            account=account,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            private=private,
        )


@list_docstring
def list_cluster_configurations(account=None):
    with Cloud() as cloud:
        return cloud.list_cluster_configurations(account=account)


@delete_docstring
def delete_cluster_configuration(name):
    with Cloud() as cloud:
        return cloud.delete_cluster_configuration(name=name)


def create_cluster(
    name: str = None,
    *,
    configuration: str,
    software: str = None,
    worker_cpu: int = None,
    worker_gpu: int = None,
    worker_memory: str = None,
    worker_class: str = None,
    worker_options: dict = None,
    scheduler_cpu: int = None,
    scheduler_memory: str = None,
    scheduler_class: str = None,
    scheduler_options: dict = None,
    account: str = None,
    workers: int = 0,
    backend_options: Optional[Dict] = None,
    environ: Optional[Dict] = None,
    log_output=sys.stdout,
) -> int:
    """Create a cluster
    Parameters
    ---------
    name
        Name of cluster.
    configuration
        Identifier of the cluster configuration to use, in the format (<account>/)<name>. If the configuration
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.
        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have a configuration
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".
    software
        Identifier of the software environment to use, in the format (<account>/)<name>. If the software environment
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.

        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have an environment
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".

        The "name" portion of (<account>/)<name> can only contain ASCII letters, hyphens and underscores.
    worker_cpu
        Number of CPUs allocated for each worker. Defaults to 2.
    worker_gpu
        Number of GPUs allocated for each worker. Defaults to 0 (no GPU support). Note that this will _always_
        allocate GPU-enabled workers, so is expensive.
    worker_memory
        Amount of memory to allocate for each worker. Defaults to 8 GiB.
    worker_class
        Worker class to use. Defaults to "dask.distributed.Nanny".
    worker_options
        Mapping with keyword arguments to pass to ``worker_class``. Defaults to ``{}``.
    scheduler_cpu
        Number of CPUs allocated for the scheduler. Defaults to 1.
    scheduler_memory
        Amount of memory to allocate for the scheduler. Defaults to 4 GiB.
    scheduler_class
        Scheduler class to use. Defaults to "dask.distributed.Scheduler".
    scheduler_options
        Mapping with keyword arguments to pass to ``scheduler_class``. Defaults to ``{}``.
    account
        Name of the Coiled account to create the cluster in.
        If not provided, will default to ``Cloud.default_account``.
    workers
        Number of workers we to launch.
    backend_options
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``). Any options
        specified with this keyword argument will take precedence over those stored in the
        ``coiled.backend-options`` cofiguration value.
    environ
        Dictionary of environment variables.
    See Also
    --------
    coiled.Cluster
    """
    # TODO cleanup repetition of explaining a configuration identifier (see docstring for
    # creating software_environments)
    warnings.warn(
        "Please use coiled.Cluster() for creating clusters instead of coiled.create_cluster()."
        "coiled.Cluster() offers more control over the cluster you create and is the recommended approach."
    )
    with Cloud(account=account) as cloud:
        return cloud.create_cluster(
            name=name,
            configuration=configuration,
            software=software,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            worker_class=worker_class,
            worker_options=worker_options,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            scheduler_class=scheduler_class,
            scheduler_options=scheduler_options,
            account=account,
            workers=workers,
            backend_options=backend_options,
            environ=environ,
            log_output=log_output,
        )


@list_docstring
def list_clusters(account=None):
    with Cloud() as cloud:
        return cloud.list_clusters(account=account)


@delete_docstring
def delete_cluster(name: str, account: str = None):
    with Cloud() as cloud:
        cluster_id = cloud.get_cluster_by_name(name=name, account=account)
        if cluster_id is not None:
            return cloud.delete_cluster(cluster_id=cluster_id, account=account)


def cluster_logs(name: str, account: str = None) -> Logs:
    """Retrieve logs from a Coiled cluster.

    Parameters
    ----------
    name
        Cluster name

    account
        The account in which the cluster is running

    Returns
    -------
    logs
        The logs from the cluster.
    """
    with Cloud() as cloud:
        cluster_id = cloud.get_cluster_by_name(name=name, account=account)
        if cluster_id is not None:
            return cloud.cluster_logs(cluster_id=cluster_id, account=account)


@experimental
def create_job_configuration(
    name: str,
    command: List[str],
    software: str,
    *,
    account: str = None,
    cpu: int = 1,
    gpu: int = 0,
    memory: str = "4 GiB",
    ports: List = None,
    files: Union[str, List[str]] = None,
    description: Optional[str] = None,
) -> None:
    """Create a job configuration

    Parameters
    ----------
    name
        Name of the job configuration
        Optionally prefixed with an account name like "myaccount/myname"
    command:
        Command to run this job. Defaults to None.
    software
        Identifier of the software environment to use, in the format (<account>/)<name>. If the software environment
        is owned by the same account as that passed into "account", the (<account>/) prefix is optional.

        For example, suppose your account is "wondercorp", but your friends at "friendlycorp" have an environment
        named "xgboost" that you want to use; you can specify this with "friendlycorp/xgboost". If you simply
        entered "xgboost", this is shorthand for "wondercorp/xgboost".
    account
        The coiled account in which to create the configuration.
    cpu
        Number of CPUs allocated for this job. Defaults to 1.
    gpu
        Number of GPUs allocated for this job. Defaults to 0.
    memory
        Ammount of memory allocated for this job. Defaults to 4 GiB.
    ports
        List of ports to expose. Defaults to None.
    files
        List of local files to upload.
    description
        Description for the job.
    """
    with Cloud() as cloud:
        return cloud.create_job_configuration(
            name=name,
            command=command,
            software=software,
            account=account,
            cpu=cpu,
            gpu=gpu,
            memory=memory,
            ports=ports,
            files=files,
            description=description,
        )


@experimental
def start_job(
    configuration: str,
    account: str = None,
    backend_options: Optional[Dict] = None,
    environ: Optional[Dict] = None,
    log_output=sys.stdout,
):
    """Start a job

    Parameters
    ----------
    configuration
        Name of the job configuration to create the job from.
    account
        Name of Coiled account to use. If not provided, will
        default to the user account for the ``cloud`` object being used.
    backend_options
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``). Any options
        specified with this keyword argument will take precedence over those stored in the
        ``coiled.backend-options`` cofiguration value
    environ
        Dictionary of environment variables.
    log_output
        Stream to output logs to. Defaults to ``sys.stdout``.
    """
    with Cloud(account=account) as cloud:
        return cloud.start_job(
            configuration=configuration,
            account=account,
            backend_options=backend_options,
            environ=environ,
            log_output=log_output,
        )


@experimental
def stop_job(name: str):
    """Stop a running job

    Parameters
    ----------
    name
        Name of job to stop.

        You can get a list of running jobs and their names by using the
        command ``coiled.list_jobs()``
    """
    with Cloud() as cloud:
        return cloud.stop_job(name=name)


@experimental
@list_docstring
def list_job_configurations(account=None):
    with Cloud(account=account) as cloud:
        return cloud.list_job_configurations(account=account)


@experimental
@delete_docstring
def delete_job_configuration(name):
    with Cloud() as cloud:
        return cloud.delete_job_configuration(name=name)


@experimental
@list_docstring
def list_jobs(account=None):
    with Cloud(account=account) as cloud:
        return cloud.list_jobs(account=account)


@experimental
def job_logs(name: str, account: str = None) -> Logs:
    """Retrieve logs from a Coiled job.

    Parameters
    ----------
    name
        Job name

    account
        The account in which the job is run

    Returns
    -------
    logs
        Coiled job logs
    """
    with Cloud() as cloud:
        job_id = cloud.get_job_by_name(name=name, account=account)
        if job_id is not None:
            return cloud.job_logs(job_id=job_id, account=account)


@experimental
def create_notebook(
    name,
    *,
    container="coiled/notebook:latest",
    conda=None,
    pip=None,
    post_build=None,
    cpu: int = 1,
    gpu: int = 0,
    memory: str = "4 GiB",
    files=None,
    command=("/bin/bash", "start.sh", "jupyter", "lab"),
    ports=(8888,),
    description=None,
    environ: Optional[Dict] = None,
):
    """Create a notebook

    This allows you to create a hosted notebook which is runnable on https://cloud.coiled.io.

    Parameters
    ---------
    name
        Name of the notebook.
    container
        Docker image to use for the notebook's software environment.
        Defaults to ``coiled/notebook:latest``. Note that when using a non-default
        container, you should check whether the default ``command`` is compatible
        with the container being used and, if not, update the ``command`` such that
        it launches a Jupyter session within the container.
    conda
        Specification for packages to install into the notebook's software environment using conda.
        Can be a list of packages, a dictionary, or a path to a conda environment YAML file.
    pip
        Packages to install into the notebook's software environment using pip.
        Can be a list of packages or a path to a pip requirements file.
    post_build
        List of commands or path to a local executable script to run after pip and conda packages
        have been installed.
    cpu
        Number of CPUs allocated for the notebook session. Defaults to 1.
    gpu
        Number of GPUs allocated for the notebook session. Defaults to 0 (no GPU support).
    memory
        Amount of memory to allocated for the notebook session. Defaults to 4 GiB.
    files
        List of local files to upload.
    command
        Command to run. If not specified, defaults to running JupyterLab.
    ports
        List of ports to expose. If not specified, defaults to ``(8888,)``
    description
        Description for notebook.
    environ
        Dictionary of environment variables.
    """

    with Cloud() as cloud:

        # Create software environment for notebook
        name_software = name + "-notebook"
        cloud.create_software_environment(
            name=name_software,
            container=container,
            conda=conda,
            pip=pip,
            post_build=post_build,
            environ=environ,
        )

        # Create job configuration for notebook
        cloud.create_job_configuration(
            name=name,
            software=name_software,
            cpu=cpu,
            gpu=gpu,
            memory=memory,
            command=command,
            files=files,
            ports=ports,
            description=description,
        )


def cluster_cost_estimate(
    n_workers: int = 4,
    configuration: str = None,
    worker_cpu: int = None,
    worker_gpu: int = None,
    worker_memory: Union[str, int] = None,
    scheduler_cpu: int = None,
    scheduler_memory: Union[str, int] = None,
    backend_options: Optional[Dict] = None,
) -> str:
    """Estimate the cluster hourly cost

    Parameters
    ----------
    n_workers
        Number of workers in this cluster. Defaults to 4.
    configuration
        Name of cluster configuration to create cluster from.
        If not specified, defaults to ``coiled/default`` for the
        current Python version.
    worker_cpu
        Number of CPUs allocated for each worker. Defaults to 1.
    worker_gpu
        Number of GPUs allocated for each worker. Defaults to 0 (no GPU support). Note that this will _always_
        allocate GPU-enabled workers, so is expensive.
    worker_memory
        Amount of memory to allocate for each worker. Defaults to 4 GiB.
    scheduler_cpu
        Number of CPUs allocated for the scheduler. Defaults to 1.
    scheduler_memory
        Amount of memory to allocate for the scheduler. Defaults to 4 GiB.
    backend_options
        Dictionary of backend specific options (e.g. ``{'region': 'us-east-2'}``). Any options
        specified with this keyword argument will take precedence over those stored in the
        ``coiled.backend-options`` cofiguration value.

    See Also
    --------
    dask.utils.parse_bytes
    """
    if configuration is None:
        v = "".join(map(str, sys.version_info[:2]))
        configuration = f"coiled/default-py{v}"
    with Cloud() as cloud:
        return cloud.cluster_cost_estimate(
            n_workers=n_workers,
            configuration=configuration,
            worker_cpu=worker_cpu,
            worker_gpu=worker_gpu,
            worker_memory=worker_memory,
            scheduler_cpu=scheduler_cpu,
            scheduler_memory=scheduler_memory,
            backend_options=backend_options,
        )


@overload
def list_core_usage(json: Literal[True], account: str = None) -> dict:
    ...


@overload
def list_core_usage(json: Literal[False] = False, account: str = None) -> None:
    ...


def list_core_usage(json: bool = False, account: str = None) -> Union[dict, None]:
    """Get a list of used cores.

    Returns a table that shows the limit of cores that the user can use
    and a breakdown of the core usage split up between account, user, clusters
    and jobs.

    Parameters
    ----------
    account
        Name of the Coiled account to list core usage. If not provided,
        will use the coiled.account configuration value.
    json
        If set to ``True``, it will return this list in json format instead of
        a table.
    """
    with Cloud() as cloud:
        return cloud.list_core_usage(json=json, account=account)


def get_notifications(
    json: bool = False,
    account: str = None,
    limit: int = 100,
    level: Union[int, str] = logging.NOTSET,
) -> Union[List[dict], None]:
    """Get a list of all recent notifications.

    Parameters
    ----------
    account
        Name of the Coiled account to list notifications. If not provided,
        will use the coiled.account configuration value.
    json
        If set to ``True``, it will return this list in json format instead of
        a table.
    limit
        The max number of notifications to return.
    level
        A constant from the standard python logging library (e.g., ``logging.INFO``),
        or a string of one of the following: ``debug``, ``info``, ``warning``, ``error``,
        or ``critical``. This will be used to filter the returned notifications.
    """
    with Cloud() as cloud:
        return cloud.get_notifications(
            json=json, account=account, limit=limit, level=level
        )


@overload
def list_local_versions(json: Literal[False] = False) -> None:
    ...


@overload
def list_local_versions(json: Literal[True]) -> dict:
    ...


def list_local_versions(json: bool = False) -> Optional[dict]:
    """Get information about local versions.

    Returns the versions of Python, Coiled, Dask and Distributed that
    are installed locally. This information could be useful when
    troubleshooting issues.

    Parameters
    ----------
    json
        If set to ``True``, it will return this list in json format instead of a
        table.
    """
    with Cloud() as cloud:
        return cloud.list_local_versions(json=json)


def diagnostics(account: str = None) -> dict:
    """Run a diagnose check aimed to help support with any issues.

    This command will call others to dump information that could help
    in troubleshooting issues. This command will return a json that will
    make it easier for you to share with the Coiled support team if needed.

    Parameters
    ----------
    account
        Name of the Coiled account to list core usage. If not provided,
        will use the coiled.account configuration value.
    """
    console = rich_console()
    with console.status("Gathering diagnostics..."):
        with Cloud() as cloud:
            data = {}

            health_check = cloud.health_check()
            status = health_check.get("status", "Issues found")

            data["health_check"] = health_check
            console.print(f"Performing health check.... Status: {status}")
            time.sleep(0.5)

            console.print("Gathering information about local environment...")
            local_versions = cloud.list_local_versions(json=True)
            data["local_versions"] = local_versions
            time.sleep(0.5)

            configuration = dask.config.config
            configuration["coiled"]["token"] = "hidden"
            data["coiled_configuration"] = configuration
            time.sleep(0.5)

            console.print("Getting user information...")
            user_info = cloud.list_user_information()
            data["user_information"] = user_info
            time.sleep(0.5)

            usage = cloud.list_core_usage(json=True, account=account)
            data["core_usage"] = usage
            time.sleep(0.5)

            return data


def list_user_information() -> dict:
    """List information about your user.

    This command will give you more information about your account,
    which teams you are part of and any limits that your account might
    have.
    """
    with Cloud() as cloud:
        cloud.list_user_information()
        return cloud.list_user_information()


def _upload_report(filename, private=False, account=None) -> dict:
    """Private method for uploading report to Coiled"""
    if not os.path.isfile(filename):
        raise ValueError("Report file does not exist.")

    statinfo = os.stat(filename)
    if statinfo.st_size >= 1048576 * 10:
        raise ValueError("Report file size greater than 10mb limit")

    # At this point Dask has generated a local file with the performance report contents
    with Cloud() as cloud:
        result = cloud.upload_performance_report(
            filename, filename=filename, private=private, account=account
        )
        return result


@experimental
@contextmanager
def performance_report(
    filename="dask-report.html",
    private=False,
    account=None,
) -> Generator[None, None, None]:
    """Generates a static performance report and saves it to Coiled Cloud

    This context manager lightly wraps Dask's performance_report. It generates a static performance
    report and uploads it to Coiled Cloud. After uploading, it prints out the url where the report is
    hosted. For a list of hosted performance reports, utilize coiled.list_performance_reports(). Note
    each user is limited to 5 hosted reports with each a maximum file size of 10mb.

    Parameters
    ----------

    filename
        The file name of the performance report file.
    private
        If set to ``True``, the uploaded performance report is only accessible to logged in Coiled users who
        are members of the current / default or specified account.
    account
        Associated the account which user wishes to upload to. If not specified, current / default
        account will be utilized.

    """

    # stacklevel= is newer kwarg after version check below
    try:
        report_kwargs = {"stacklevel": 3} if DISTRIBUTED_VERSION >= "2021.05.0" else {}
        with dask.distributed.performance_report(filename=filename, **report_kwargs):
            yield
    except Exception as ex:
        raise Exception(
            "Exception in coiled.performance_report() context"
        ).with_traceback(ex.__traceback__)
    finally:
        results = _upload_report(filename, private=private, account=account)
        console = Console()
        text = Text(
            f'Performance Report Available at: {results["url"]}',
            style=f"link {results['url']}",
        )
        console.print(text)


@experimental
def list_performance_reports(account=None) -> List[Dict]:
    """List performance reports stored on Coiled Cloud

    Returns a list of dicts that contain information about Coiled Cloud hosted performance reports

    Parameters
    ----------

    account
        Associated account for which the user wishes to get reports from. If not specified, current / default
        account will be utilized.

    """
    with Cloud() as cloud:
        result = cloud.list_performance_reports(account=account)
        return result


def _parse_gcp_creds(
    gcp_service_creds_dict: Optional[Dict], gcp_service_creds_file: Optional[str]
) -> Dict:
    if not any([gcp_service_creds_dict, gcp_service_creds_file]):
        raise GCPCredentialsParameterError(
            "Parameter 'gcp_service_creds_file' or 'gcp_service_creds_dict' must be supplied"
        )

    if gcp_service_creds_file:
        if not os.path.isfile(gcp_service_creds_file):
            raise GCPCredentialsError(
                "The parameter 'gcp_service_creds_file' must be a valid file"
            )
        try:
            with open(gcp_service_creds_file, "r") as json_file:
                creds = json.load(json_file)

                required_keys = [
                    "type",
                    "project_id",
                    "private_key_id",
                    "private_key",
                    "client_email",
                    "client_id",
                    "auth_uri",
                    "token_uri",
                    "auth_provider_x509_cert_url",
                    "client_x509_cert_url",
                ]
                missing_keys = [key for key in required_keys if key not in creds]
                if missing_keys:
                    raise GCPCredentialsError(
                        message=(
                            f"The supplied file '{gcp_service_creds_file}' is missing the keys: "
                            f"{', '.join(missing_keys)}"
                        )
                    )

                return creds
        except JSONDecodeError:
            raise GCPCredentialsError(
                f"The supplied file '{gcp_service_creds_file}' is not a valid JSON file."
            )
    if gcp_service_creds_dict and not gcp_service_creds_dict.get("project_id"):
        raise GCPCredentialsError(
            "Unable to find 'project_id' in 'gcp_service_creds_dict', make sure this key exists in the dictionary"
        )

    # Type checker doesn't know that this should no longer
    # be None.
    return cast(Dict, gcp_service_creds_dict)


@experimental
def set_backend_options(
    use_coiled_defaults: bool = False,
    account: str = None,
    backend: Literal["aws", "azure", "gcp", "ecs"] = "aws",
    create_vpc: bool = False,
    aws_region: str = "us-east-1",
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    gcp_service_creds_file: str = None,
    gcp_service_creds_dict: dict = None,
    gcp_project_id: str = None,
    gcp_region: Optional[str] = None,
    gcp_zone: Optional[str] = None,
    azure_resource_group: str = None,
    azure_client_id: str = None,
    azure_secret: str = None,
    azure_subscription_id: str = None,
    azure_tenant: str = None,
    azure_region: str = "eastus",
    registry_type: Literal["ecr", "docker_hub", "gar", "acr"] = "ecr",
    registry_namespace: str = None,
    registry_access_token: str = None,
    registry_uri: str = "docker.io",
    registry_username: str = None,
    log_output=sys.stdout,
    **kwargs,
):
    """Configure account level settings for cloud provider and container registry.

    This method configures account level backend settings for cloud providers, container registries,
    and setting up an account-level VPC for running clusters and other Coiled managed resources.


    Parameters
    ----------

    use_coiled_default
        Boolean to reset backend options to Coiled default settings which are for the AWS VM
        backend with default region of us-east-1.

    account
        Coiled account to configure if user has access. If not specified, current / default
        account will be utilized.

    backend_type
        Supported backends such as AWS VM (vm_aws), AWC ECS (ecs), GCP VM (vm_gcp) and Azure VM (vm_azure).

    create_vpc
        For supported backends, when create_vpc=True options will create a VPC (or reuse an existing one) inside of the
        user account of the specified region for the cloud provider credentials supplied. Note that supplying valid
        credentials for cloud provider is required for Coiled to manage the setup, configure and access policies for
        users of this account.

    aws_region
        The region which Coiled cloud resources will be deployed to and where other resources
        such as the docker registry are located or where a specified VPC will be created.

    aws_access_key_id
        For AWS support backend, this argument is required to create or use an existing Coiled managed VPC.

    aws_secret_access_key
        For AWS support backend, this argument is required to create or use an existing Coiled managed VPC.

    gcp_service_creds_file
        A string filepath to a Google Cloud Compute service account json credentials file used for creating and
        managing a Coiled VPC.

    gcp_service_creds_dict
        A dictionary of the contents of a Google Cloud Compute service account json credentials file used for
        creating a VPC to host Coiled Cloud related assets.

    gcp_project_id
        The Google Cloud Compute project id in which a VPC will be created to host Coiled Cloud related assets.

    gcp_region
        The Google Cloud Compute region name in which a VPC will be created.

    gcp_zone
        The Google Cloud Compute zone name in which a subnet will be create (Zone should be <region>-<zone letter>)
        for example zone C for ``us-east1`` should be specified as ``us-east1-c``.

    azure_resource_group
        The Azure resource name where the cluster will be created.

    azure_client_id
        The Azure clientId credential

    azure_secret
        The Azure clientSecret credential

    azure_subscription_id
        The Azure subscriptionId

    azure_tenant
        The Azure tenantId

    azure_region
        An Azure region.

    registry_type
        Custom software environments are stored in a docker container registry. By default, container images will be
        stored in AWS ECR. Users are able to store contains on a private registry by providing additional
        configuration registry_* arguments and specifying registry_type='docker_hub'. To use
        Google Artifact Registry, pass registry_type='gar', gcp_project_name, gcp_region_name,
        and one of gcp_service_creds_dict or gcp_service_creds_file. To use Azure Container Registry, pass
        registry_type='acr', azure_resource_group, azure_client_id, azure_secret, azure_subscription_id,
        azure_tenant, and azure_region.

    registry_uri
        The container registry URI. Defaults to docker.io. Only required if
        registry_type='docker_hub'.

    registry_username
        A registry username (should be lowercased). Only required if
        registry_type='docker_hub'.

    registry_namespace
        A namespace for storing the container images. Defaults to username if not specified. More information
        about docker namespaces can be found here: https://docs.docker.com/docker-hub/repos/#creating-repositories.
        Only required if registry_type='docker_hub'.

    registry_access_token
        A token to access registry images. More information about access tokens ca be found here:
        https://docs.docker.com/docker-hub/access-tokens/. Only required if registry_type='docker_hub'.

    """
    # TODO - see if way to add default in BE to avoid re-versioning of this
    backend_options = {
        "backend": "vm_aws",
        "options": {
            "aws_region_name": aws_region,
            "account_role": "",
            "credentials": {"aws_access_key_id": "", "aws_secret_access_key": ""},
        },
        "registry": {"type": "ecr", "credentials": {}, "public_ecr": False},
    }

    # TODO Provide Backwards compatibility to old keywords remove once experimental is removed
    region = kwargs.get("region")
    if region:
        aws_region = region
    backend_type = kwargs.get("backend_type")
    if backend_type:
        backend = backend_type
    gcp_project_name = kwargs.get("gcp_project_name")
    if gcp_project_name:
        gcp_project_id = gcp_project_name
    gcp_region_name = kwargs.get("gcp_region_name")
    if gcp_region_name:
        gcp_region = gcp_region_name

    output_msg = ""
    # Used to print warnings to the user
    console = Console()

    supported_backends = {"aws", "azure", "gcp", "ecs"}
    if backend not in supported_backends:
        raise UnsupportedBackendError(
            f"Supplied backend: {backend} not in supported types: {supported_backends}"
        )

    if aws_access_key_id and aws_secret_access_key:
        # verify that these are vaild credentials
        verify_aws_credentials(aws_access_key_id, aws_secret_access_key)

    azure_required_kwargs = {
        "azure_resource_group": azure_resource_group,
        "azure_client_id": azure_client_id,
        "azure_secret": azure_secret,
        "azure_subscription_id": azure_subscription_id,
        "azure_tenant": azure_tenant,
        "azure_region": azure_region,
    }

    # Can be used for azure backend validation, and error display
    missing_azure_kwargs = ", ".join(
        [kw for kw, val in azure_required_kwargs.items() if not val]
    )

    parsed_gcp_credentials: Optional[Dict] = None

    # Parse GCP region/zones or return default region/zone
    gcp_region, gcp_zone = parse_gcp_region_zone(region=gcp_region, zone=gcp_zone)
    if use_coiled_defaults is True:
        # use default options
        output_msg = "Successfully, set your backend options to Coiled Defaults."
        pass
    elif backend == "ecs":
        if aws_access_key_id and aws_secret_access_key or create_vpc:
            raise UnsupportedBackendError("VPC for AWS ECS is no longer supported.")
        else:
            backend_options["backend"] = "ecs"
            backend_options["options"]["region"] = aws_region
            output_msg = "Successfully, set your backend options to Coiled ECS on AWS."

    elif backend == "aws":
        if create_vpc:
            backend_options["backend"] = "vm"
            backend_options["options"]["aws_region_name"] = aws_region
            if aws_access_key_id and aws_secret_access_key:
                backend_options["options"]["credentials"] = {
                    "aws_access_key": aws_access_key_id,
                    "aws_secret_key": aws_secret_access_key,
                }

                backend_options["options"]["provider_name"] = "aws"
                backend_options["options"]["type"] = "aws_cloudbridge_backend_options"
                output_msg = "Successfully, set your backend options to Coiled Customer Hosted on AWS VM."
            else:
                raise AWSCredentialsParameterError(
                    "Creating an AWS VPC requires params: aws_access_key_id and aws_secret_access_key."
                )
        else:
            if aws_secret_access_key and aws_access_key_id:
                warning_message = Text(
                    text=(
                        "WARNING: Credentials provided without using 'create_vpc=True', please use this "
                        "parameter if you want to use Coiled on your AWS account. \n"
                    ),
                    style="yellow",
                )
                console.print(warning_message)
            backend_options["backend"] = "vm_aws"
            backend_options["options"]["aws_region_name"] = aws_region
            output_msg = (
                "Successfully, set your backend options to Coiled Hosted on AWS VM."
            )
    elif backend == "gcp":
        if create_vpc:
            parsed_gcp_credentials = _parse_gcp_creds(
                gcp_service_creds_dict=gcp_service_creds_dict,
                gcp_service_creds_file=gcp_service_creds_file,
            )
            if not gcp_project_id:
                gcp_project_id = parsed_gcp_credentials.get("project_id", "")
            backend_options["options"][
                "gcp_service_creds_dict"
            ] = parsed_gcp_credentials

            backend_options["backend"] = "vm"

            backend_options["options"]["provider_name"] = "gcp"
            backend_options["options"]["type"] = "gcp_cloudbridge_backend_options"

            backend_options["options"]["gcp_project_name"] = gcp_project_id
            backend_options["options"]["gcp_region_name"] = gcp_region
            backend_options["options"]["gcp_zone_name"] = gcp_zone

            output_msg = "Successfully set your backend options to Coiled Customer Hosted on GCP VM."

        else:
            if gcp_service_creds_dict or gcp_service_creds_file:
                warning_message = Text(
                    text=(
                        "WARNING: Credentials provided without using 'create_vpc=True', please use this "
                        "parameter if you want to use Coiled on your GCP account. \n"
                    ),
                    style="yellow",
                )
                console.print(warning_message)
            backend_options["backend"] = "vm_gcp"
            if gcp_region:
                backend_options["options"] = {
                    "gcp_region_name": gcp_region,
                    "gcp_zone_name": gcp_zone,
                }
            else:
                backend_options["options"] = {}

            output_msg = (
                "Successfully set your backend options to Coiled Hosted on GCP VM."
            )

    elif backend == "azure":
        if create_vpc:

            if missing_azure_kwargs:
                raise AzureCredentialsParameterError(
                    f"Missing Azure parameters: {missing_azure_kwargs}"
                )

            backend_options["backend"] = "vm"
            backend_options["options"]["provider_name"] = "azure"
            backend_options["options"]["type"] = "azure_cloudbridge_backend_options"

            backend_options["options"]["azure_region_name"] = azure_region
            backend_options["options"]["azure_resource_group"] = azure_resource_group
            backend_options["options"]["azure_client_id"] = azure_client_id
            backend_options["options"]["credentials"]["azure_secret"] = azure_secret
            backend_options["options"]["credentials"][
                "azure_subscription_id"
            ] = azure_subscription_id
            backend_options["options"]["credentials"]["azure_tenant"] = azure_tenant
            output_msg = "Successfully, set your backend options to Coiled Customer Hosted on Azure VM."
        else:
            if any(
                [
                    azure_resource_group,
                    azure_client_id,
                    azure_secret,
                    azure_subscription_id,
                    azure_tenant,
                ]
            ):
                warning_message = Text(
                    text=(
                        "WARNING: Credentials provided without using 'create_vpc=True', please use this "
                        "parameter if you want to use Coiled on your Azure account. \n"
                    ),
                    style="yellow",
                )
                console.print(warning_message)
            backend_options["backend"] = "vm_azure"
            backend_options["options"] = {"azure_region_name": azure_region}
            output_msg = (
                "Successfully, set your backend options to Coiled Hosted on Azure VM."
            )

    ### container registry
    if use_coiled_defaults is True:
        pass
    elif registry_type == "ecr":
        # TODO add aws credentials in here for VPCs
        backend_options["registry"]["region"] = aws_region
        if aws_access_key_id and aws_secret_access_key:
            backend_options["registry"]["credentials"][
                "aws_access_key_id"
            ] = aws_access_key_id
            backend_options["registry"]["credentials"][
                "aws_secret_access_key"
            ] = aws_secret_access_key

    elif registry_type == "docker_hub":
        registry = {
            "account": registry_namespace or registry_username,
            "password": registry_access_token,
            "type": registry_type,
            "uri": registry_uri,
            "username": registry_username,
        }

        # any missing values
        empty_registry_values = [f"registry_{k}" for k, v in registry.items() if not v]
        if any(empty_registry_values):
            raise RegistryParameterError(
                f"For setting your registry credentials, these fields cannot be empty: {empty_registry_values}"
            )

        # docker username /// account name cannot be uppercase
        if (
            registry_username
            and any(ele.isupper() for ele in registry_username) is True
        ):
            raise RegistryParameterError(
                "Your dockerhub [registry_username] must be lowercase"
            )

        backend_options["registry"] = registry
    elif registry_type == "gar":
        if parsed_gcp_credentials is None:
            parsed_gcp_credentials = _parse_gcp_creds(
                gcp_service_creds_dict=gcp_service_creds_dict,
                gcp_service_creds_file=gcp_service_creds_file,
            )
        if not gcp_project_id:
            gcp_project_id = parsed_gcp_credentials.get("project_id", "")
        gar_required_kwargs = {
            "gcp_region_name": gcp_region,
            "gcp_project_name": gcp_project_id,
            "one of gcp_service_creds_dict / gcp_service_creds_file": parsed_gcp_credentials,
        }
        missing_gar_kwargs = ", ".join(
            [kw for kw, val in gar_required_kwargs.items() if not val]
        )
        if missing_gar_kwargs:
            raise RegistryParameterError(
                f"Missing required args for Google Artifact Registry: {missing_gar_kwargs}"
            )
        backend_options["registry"] = {
            "type": registry_type,
            "location": gcp_region,
            "project_id": gcp_project_id,
            "credentials": parsed_gcp_credentials,
        }
    elif registry_type == "acr":
        if missing_azure_kwargs:
            raise RegistryParameterError(
                f"Missing Azure parameters: {missing_azure_kwargs}"
            )
        backend_options["registry"] = {
            "type": registry_type,
            "credentials": azure_required_kwargs,
            "location": azure_region,
        }

    with Cloud(account=account) as cloud:
        account_options_url = cloud.set_backend_options(
            backend_options,
            account=account,
            log_output=log_output,
        )

        text = Text()
        text.append(output_msg, style="green")
        text.append("\n\n")
        text.append(
            f"Please confirm your account backend options here: {account_options_url}",
            style=f"link {account_options_url}",
        )
        console.print(text)
