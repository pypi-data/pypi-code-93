

import sys
import requests
import pypistats
import json
import yaml
import pyaml
from pprint import pprint
from collections import OrderedDict
from typing import Optional, Tuple, List


def _req(
        path:   str,
        method: str,
        data:   Optional[dict]
) -> Tuple[int, dict]:

    r = {
        'GET': lambda p, *_: requests.get(p),
        'POST': lambda p, d, *_: requests.post(p, data=d),
    }.get(method, lambda *_: None)(path, data)

    return r.status_code, r.json()


# not used anywhere
def post(path: str, data: Optional[dict]):
    return _req(path, 'POST')


def package_download_stats(package: str):

    recent = json.loads(pypistats.recent(package, format='json')).get('data', {})
    overall = json.loads(pypistats.overall(package, mirrors=True, format='json')).get('data', [])[0]

    downloads = {
        'last_day': recent.get('last_day'),
        'last_week': recent.get('last_week'),
        'last_month': recent.get('last_month'),
        'total': overall.get('downloads'),
    }

    major = pypistats.python_major(package, format='json')
    minor = pypistats.python_minor(package, format='json')

    return downloads


def nullish_add_to_dict(d: dict, key, val):
    if not key or not val:
        return
    d[key] = val


def pypi_page_lookup(packages: List[str]):

    d = {}


    for p in packages:
        r = _req(f'https://pypi.org/pypi/{p}/json', 'GET', {})[1]
        # print(r, type(r))
        info = r.get('info', {})

        data = {
            'description': info.get('description')[:200],
            'license': info.get('license'),
            'downloads': package_download_stats(p),
            'package_version': info.get('version'),
            'python_version': '.'.join(map(lambda x: str(x), sys.version_info)),
            'last_releases': '; '.join(list(r.get('releases').keys())[-1:-6:-1])
        }

        nullish_add_to_dict(data, 'name', info.get('name'))
        nullish_add_to_dict(data, 'author', info.get('author'))
        nullish_add_to_dict(data, 'mail', info.get('author_email'))
        nullish_add_to_dict(data, 'summary', info.get('summary'))

        if bugtrack := info.get('bugtrack_url'):
            data['bugs'] = bugtrack

        if page := info.get('home_page'):
            data['page'] = page

        if maintainer := info.get('maintainer'):
            data['maintainer'] = maintainer

        if maintainer_email := info.get('maintainer_email'):
            data['maintainer_email'] = maintainer

        if docs_page := info.get('docs_url'):
            data['docs_page'] = docs_page

        if package_page := info.get('package_url'):
            data['package_page'] = package_page

        d[p] = data

    return d


def show_stats(*packages: str):
    for p in packages:

        p_info = pypi_page_lookup(p)
        p_ordered = OrderedDict(p_info)

        pyaml.dump(p_ordered, sys.stdout,
                         indent=3, width=120, vspacing=[1, 0])
        print()
