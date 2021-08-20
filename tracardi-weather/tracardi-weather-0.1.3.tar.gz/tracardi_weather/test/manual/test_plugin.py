import asyncio
from tracardi.domain.profile import Profile

from tracardi_weather.plugin import WeatherAction


async def main():
    plugin = WeatherAction(**{
        "system": "metric"
    })

    plugin.profile = Profile(
        id="1"
    )
    plugin.profile.traits.public['city'] = "Paris"

    result = await plugin.run(**{
        "city": "Wrocław"
    })

    print(result)

    result = await plugin.run(**{
        "city": "profile@traits.public.city"
    })

    print(result)


asyncio.run(main())
