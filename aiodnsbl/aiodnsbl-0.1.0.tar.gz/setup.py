# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiodnsbl']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0', 'idna>=3.2,<4.0', 'poetry-version>=0.1.5,<0.2.0']

setup_kwargs = {
    'name': 'aiodnsbl',
    'version': '0.1.0',
    'description': 'Async DNSBL lists checker',
    'long_description': '# aiodnsbl\n\n[DNSBL](https://en.wikipedia.org/wiki/DNSBL) lists checker based on [aiodns](https://github.com/saghul/aiodns). Checks if an IP or a domain is listed on anti-spam DNS blacklists.\n\n## Notes\n\nThis is a fork of [pydnsbl](https://github.com/dmippolitov/pydnsbl).\n\nKey differences:\n\n- Fully type annotated\n- No sync wrapper (async only)\n- No category classification\n\n## Installation\n\n```bash\npip install aiodnsbl\n```\n\n## Usage\n\n```python\nimport asyncio\n\nfrom aiodnsbl import DNSBLChecker\n\n\nloop = asyncio.get_event_loop()\n\nchecker = DNSBLChecker()\n\n# Check IP\nloop.run_until_complete(checker.check("8.8.8.8"))\n# <DNSBLResult: 8.8.8.8  (0/10)>\nloop.run_until_complete(checker.check("68.128.212.240"))\n# <DNSBLResult: 68.128.212.240 [BLACKLISTED] (4/10)>\n\n# Check domain\nloop.run_until_complete(checker.check("example.com"))\n# <DNSBLResult: example.com  (0/4)>\n\n# Bulk check\nloop.run_until_complete(\n    checker.bulk_check(["example.com", "8.8.8.8", "68.128.212.240"])\n)\n# [<DNSBLResult: example.com  (0/4)>, <DNSBLResult: 8.8.8.8  (0/10)>, <DNSBLResult: 68.128.212.240 [BLACKLISTED] (4/10)>]\n```\n\n```python\nimport asyncio\n\nfrom aiodnsbl import DNSBLChecker\n\n\nasync def main():\n    checker = DNSBLChecker()\n    res = await checker.check("68.128.212.240")\n    print(res)\n    # <DNSBLResult: 68.128.212.240 [BLACKLISTED] (4/10)>\n    print(res.blacklisted)\n    # True\n    print([provider.host for provider in res.providers])\n    # [\'b.barracudacentral.org\', \'bl.spamcop.net\', \'dnsbl.sorbs.net\', \'ips.backscatterer.org\', ...]\n    print([provider.host for provider in res.detected_by])\n    # [\'b.barracudacentral.org\', \'dnsbl.sorbs.net\', \'spam.dnsbl.sorbs.net\', \'zen.spamhaus.org\']\n\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main())\n```',
    'author': 'Manabu Niseki',
    'author_email': 'manabu.niseki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ninoseki/aiodnsbl',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
