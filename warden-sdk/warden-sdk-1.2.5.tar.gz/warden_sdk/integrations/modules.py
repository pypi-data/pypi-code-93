from __future__ import absolute_import

from warden_sdk.hub import Hub
from warden_sdk.integrations import Integration
from warden_sdk.scope import add_global_event_processor

from typing import Any
from typing import Dict
from typing import Tuple
from typing import Iterator

_installed_modules = None

def _generate_installed_modules() -> Iterator[Tuple[str, str]]:
    try:
        import pkg_resources
    except ImportError:
        return

    # pylint: disable=not-an-iterable
    for info in pkg_resources.working_set:
        yield info.key, info.version


def _get_installed_modules() -> Dict[str, str]:
    global _installed_modules
    if _installed_modules is None:
        _installed_modules = dict(_generate_installed_modules())
    return _installed_modules


class ModulesIntegration(Integration):
    identifier = "modules"

    @staticmethod
    def setup_once() -> None:
        @add_global_event_processor
        def processor(event, hint):
            if event.get("type") == "transaction":
                return event

            if Hub.current.get_integration(ModulesIntegration) is None:
                return event

            event["modules"] = _get_installed_modules()
            return event
