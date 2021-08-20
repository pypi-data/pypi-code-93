import aiohttp
import requests
import asyncio
import json
try:
    from packaging.version import parse
except ImportError:
    print("------------------------------------- Started Installing required Canvacord Package")
    from pip._vendor.packaging.version import parse
    print("------------------------------------- Finished Installing required Canvacord Package")

thisversion = "0.2.35"

async def checkversion():
        #url_pattern = 'https://pypi.python.org/pypi/canvacord/json'
        #req = requests.get(url_pattern)
        #version = parse('0')
        #if req.status_code == requests.codes.ok:
            #j = json.loads(req.text.encode(req.encoding))
            #releases = j.get('releases', [])
            #for release in releases:
                #ver = parse(release)
                #if not ver.is_prerelease:
                    #version = max(version, ver)
            #if newresponse == thisversion:
                #pass
            #else:
                #print(f"Canvacord is on Version {newresponse} but you are only on Version {thisversion} Please Update for all the newest bug fixes and features!") 
        #else:
            pass