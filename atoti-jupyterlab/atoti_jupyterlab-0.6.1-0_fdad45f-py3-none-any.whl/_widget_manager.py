from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Union
from uuid import uuid4

from atoti._ipython_utils import running_in_ipython
from atoti.experimental.distributed.session import DistributedSession
from atoti.query.session import QuerySession
from atoti.session import Session

from ._comm_targets import WIDGET_COMM_TARGET_NAME
from ._link import get_session_location
from ._mime_types import WIDGET_MIME_TYPE

if TYPE_CHECKING:
    from ipykernel.ipkernel import IPythonKernel

_Session = Union[Session, DistributedSession, QuerySession]


@dataclass(frozen=True)
class Cell:
    """Hold some details about the notebook cell currently being executed."""

    has_built_widget: bool
    id: str


class WidgetManager:
    """Manage Jupyter comms and keep track of the widget state coming from kernel requests."""

    _cell: Optional[Cell] = None
    _running_in_supported_kernel: bool = False

    def __init__(self):
        """Create the manager."""
        if not running_in_ipython():
            return

        from IPython import get_ipython

        ipython = get_ipython()

        if not hasattr(ipython, "kernel") or not hasattr(
            ipython.kernel, "comm_manager"
        ):
            # When run from IPython or another less elaborated environment
            # than JupyterLab, these attributes might be missing.
            # In that case, there is no need to register anything.
            return

        self._running_in_supported_kernel = True

        kernel = ipython.kernel

        self._wrap_execute_request_handler_to_extract_widget_details(kernel)

    def display_widget(self, session: _Session, name: Optional[str]):
        """Display the output that will lead the atoti JupyterLab extension to show a widget."""
        if not self._running_in_supported_kernel:
            print(
                "atoti widgets can only be shown in JupyterLab with the atoti JupyterLab extension enabled."
            )
            return

        from ipykernel.comm import Comm
        from IPython.display import publish_display_data

        publish_display_data(
            {
                "text/plain": f"""Open the notebook in JupyterLab with the atoti extension enabled to {"see" if self._cell and self._cell.has_built_widget else "build"} this widget.""",
                WIDGET_MIME_TYPE: {
                    "name": name,
                    "sessionId": session._id,
                    "sessionLocation": get_session_location(session),
                    "widgetCreationCode": session._get_widget_creation_code(),
                },
            }
        )

        if self._cell is None:
            return

        widget_id = str(uuid4())

        Comm(
            WIDGET_COMM_TARGET_NAME,
            # The data below is either sensitive (e.g. auth headers) or change from one cell run to the other.
            # It is better to not send it through publish_display_data so that it does not end up in the .ipynb file.
            data={
                "cellId": self._cell.id,
                "sessionHeaders": session._generate_auth_headers(),
                "widgetId": widget_id,
            },
        ).close()

        if not isinstance(session, (Session, DistributedSession)):
            return

        session._java_api.block_until_widget_loaded(widget_id)

    def _wrap_execute_request_handler_to_extract_widget_details(
        self, kernel: IPythonKernel  # type: ignore
    ):
        original_handler = kernel.shell_handlers["execute_request"]

        def execute_request(  # pylint: disable=too-many-positional-parameters
            stream: Any, ident: Any, parent: Any
        ) -> Any:
            metadata = parent["metadata"]
            cell_id = metadata.get("cellId")
            self._cell = (
                Cell(bool(metadata.get("atoti", {}).get("state")), cell_id)
                if cell_id is not None
                else None
            )

            return original_handler(stream, ident, parent)

        kernel.shell_handlers["execute_request"] = execute_request
