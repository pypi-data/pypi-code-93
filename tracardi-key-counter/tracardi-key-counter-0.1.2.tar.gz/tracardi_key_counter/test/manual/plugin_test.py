import asyncio
from tracardi.domain.profile import Profile

from tracardi_key_counter.plugin import KeyCounterAction

init = {
    'path': 'profile@stats.counters.MobileVisits'
}

payload = {
    "payload": ['mobile', 'desktop']
}


async def main():
    plugin = KeyCounterAction(**init)

    plugin.profile = Profile(id="1")
    plugin.profile.stats.counters['MobileVisits'] = {'mobile': 1}

    result = await plugin.run(**payload)
    print(result)

asyncio.run(main())
