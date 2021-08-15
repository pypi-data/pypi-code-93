import requests
response = requests.get('http://web.archive.org/cdx/search/cdx?url=bankofamerica.com', verify=False, timeout=60)
print(response, '\n', response.content)