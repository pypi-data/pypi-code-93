from argus_cli.plugin import create_module, import_external_plugins
from argus_plugins.api_provider import argus_api

__all__ = [
    "assets",
    "cases",
    "customer_networks",
    "datastore",
    "events",
    "reports",
]

# Initialize the toolbelt with the framework.
argus_cli_module = create_module(providers=[argus_api])
