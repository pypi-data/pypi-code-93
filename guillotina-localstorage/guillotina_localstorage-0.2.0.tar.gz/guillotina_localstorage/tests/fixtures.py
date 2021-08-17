from guillotina import testing
from guillotina.tests.fixtures import ContainerRequesterAsyncContextManager

import json
import pytest


def base_settings_configurator(settings):
    if "applications" in settings:
        settings["applications"].append("guillotina_localstorage")
    else:
        settings["applications"] = ["guillotina_localstorage"]


testing.configure_with(base_settings_configurator)


class CustomRequester(ContainerRequesterAsyncContextManager):  # noqa
    async def __aenter__(self):
        await super().__aenter__()
        await self.requester(
            "POST",
            "/db/guillotina/@addons",
            data=json.dumps({"id": "guillotina_localstorage"}),
        )
        return self.requester


@pytest.fixture(scope="function")
async def custom_requester(guillotina):
    return CustomRequester(guillotina)
