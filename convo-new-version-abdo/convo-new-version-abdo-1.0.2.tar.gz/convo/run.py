import logging
import typing
from typing import Dict, Text

import convo.shared.utils.common
from convo.shared.utils.cli import printing_warning
from convo.shared.constants import DOCUMENTS_BASE_URL
from convo.core.lock_store import LockStore

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from convo.core.agent import CoreAgent


def run(
    model: Text,
    endpoints: Text,
    connector: Text = None,
    credentials: Text = None,
    **kwargs: Dict,
):
    """Runs a Convo model.

    Args:
        model: Path to model archive.
        endpoints: Path to endpoints file.
        connector: Connector which should be use (overwrites `credentials`
        field).
        credentials: Path to channel credentials file.
        **kwargs: Additional arguments which are passed to
        `convo.core.run.serve_application`.

    """
    import convo.core.run
    import convo.nlu.run
    from convo.core.utils import AvailableEndpoints
    import convo.utils.common as utils

    _endpoints = AvailableEndpoints.read_last_points(endpoints)

    if not connector and not credentials:
        connector = "rest"
        printing_warning(
            f"No chat connector configured, falling back to the "
            f"REST input channel. To connect your bot to another channel, "
            f"read the docs here: {DOCUMENTS_BASE_URL}/messaging-and-voice-channels"
        )

    kwargs = convo.shared.utils.common.min_kwargs(
        kwargs, convo.core.run.serve_app
    )
    convo.core.run.serve_app(
        model,
        run_channel=connector,
        credentials=credentials,
        endpoints=_endpoints,
        **kwargs,
    )


def create_new_agent(model: Text, endpoints: Text = None) -> "CoreAgent":
    from convo.core.tracker_store import TrackerStorage
    from convo.core.utils import AvailableEndpoints
    from convo.core.agent import CoreAgent
    from convo.core.brokers.broker import CoreEventBroker

    _endpoints = AvailableEndpoints.read_last_points(endpoints)

    _broker = CoreEventBroker.generate(_endpoints.event_broker)
    _tracker_store = TrackerStorage.create(_endpoints.tracker_store, event_broker=_broker)
    _lock_store = LockStore.create(_endpoints.lock_store)

    return CoreAgent.load(
        model,
        generator=_endpoints.nlg,
        tracker_store=_tracker_store,
        lock_store=_lock_store,
        action_endpoint=_endpoints.action,
    )
