"""
DiscordStatusPy - async API wrapper around discordstatus.com

While you can access API by directly using appropriate functions defined here,
it's better performance-wise if you use the APIClient class,
especially if you're making multiple calls.

Always close connection when you don't need your APIClient instance anymore.
For that call its `close` method:
    await my_client.close()
Or use an async content manager which will do that for you:
    async with APIClient() as client:
        # do stuff


Example 1:

import asyncio
import DiscordStatusPy

async def main():
    maintenances = await DiscordStatusPy.get_maintenances()
    print(maintenances['scheduled_maintenances'])

asyncio.run(main())

Example 2:

import asyncio
from DiscordStatusPy import APIClient

async def main():
    async with APIClient() as client:
        status = await client.get_status()
        incidents = await client.get_incidents()
        print(status['status']['description'])
        print(incidents)

asyncio.run(main())
"""

from .client import APIClient

__title__ = "DiscordStatusPy"
__author__ = "Booplicate"
__version__ = "0.0.2"


async def get_summary(**kwargs):
    """
    Get a summary of the status page, including a status indicator, component statuses,
        unresolved incidents, and any upcoming or in-progress scheduled maintenances.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_summary()

async def get_status(**kwargs):
    """
    Get the status rollup for the whole page. This endpoint includes an indicator - one of
        none, minor, major, or critical, as well as a human description of
        the blended component status.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_status()

async def get_components(**kwargs):
    """
    Get the components for the page. Each component is listed along with its status.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_components()

async def get_incidents(**kwargs):
    """
    Get a list of the 50 most recent incidents. This includes all unresolved incidents.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_incidents()

async def get_unresolved_incidents(**kwargs):
    """
    Get a list of any unresolved incidents.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_unresolved_incidents()

async def get_maintenances(**kwargs):
    """
    Get a list of the 50 most recent scheduled maintenances.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_maintenances()

async def get_upcoming_maintenances(**kwargs):
    """
    Get a list of any upcoming maintenances.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_upcoming_maintenances()

async def get_active_maintenances(**kwargs):
    """
    Get a list of any active maintenances.

    IN:
        kwargs - kwargs for APIClient

    OUT:
        dict
    """
    async with APIClient(**kwargs) as api_client:
        api_client: APIClient
        return await api_client.get_active_maintenances()
