import pytest as pytest
from tracardi.domain.profile import Profile
from tracardi_key_counter.plugin import KeyCounterAction


@pytest.mark.asyncio
async def test_plugin():

    init = {
        'path': 'profile@stats.counters.MobileVisits'
    }

    payload = {
        "payload": ['mobile', 'desktop']
    }

    plugin = KeyCounterAction(**init)

    plugin.profile = Profile(id="1")
    plugin.profile.stats.counters['MobileVisits'] = {'mobile': 1}

    result = await plugin.run(**payload)

    assert result.value == {'mobile': 2, 'desktop': 1}
