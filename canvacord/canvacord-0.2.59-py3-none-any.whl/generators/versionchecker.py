import aiohttp
import requests
import asyncio
import json
try:
    from packaging.version import parse
except ImportError:
    print("\n Started Installing required Canvacord Package")
    from pip._vendor.packaging.version import parse
    print("\n Finished Installing required Canvacord Package")

thisversion = "0.2.56"

async def checkversion():
        url_pattern = 'https://pypi.python.org/pypi/canvacord/json'
        req = requests.get(url_pattern)
        version = parse('0')
        try:
            j = json.loads(req.text.encode("utf-8"))
            releases = j.get('releases', [])
            for release in releases:
                ver = parse(release)
                if not ver.is_prerelease:
                    version = str(max(version, ver))
            splitversion = version.split(".")
            splitthisversion = thisversion.split(".")
            if version == thisversion:
                pass
            else:
                print(splitversion)
                print(splitthisversion)
                print(type(splitversion[0]))
                print(type(splitthisversion[9]))
                if int(splitversion[0]) > int(splitthisversion[0]):
                    print(f"Canvacord is on Version {version} but you are only on Version {thisversion} Please Update for all the newest bug fixes and features!")
                elif int(splitversion[1]) > int(splitthisversion[1]):
                    print(f"Canvacord is on Version {version} but you are only on Version {thisversion} Please Update for all the newest bug fixes and features!")
                elif int(splitversion[2]) > int(splitthisversion[2]):
                    print(f"Canvacord is on Version {version} but you are only on Version {thisversion} Please Update for all the newest bug fixes and features!")
                else:
                    pass
        except Exception as e:
            print(e)
            pass