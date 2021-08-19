# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['doc2pdf']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'doc2pdf',
    'version': '0.2.0',
    'description': 'A package to convert Doc files to PDF.',
    'long_description': '# Doc2PDF\n\n## Dependencies\nI recommend complete install libreoffice-writer, to minimize errors on convert.\n* Ubuntu/Debian\n```bash\napt install libreoffice-writer -y\n```\n* Alpine\n```bash\napk add libreoffice-writer\n```\n* Windows\n\nDownload from https://www.libreoffice.org/download/download/',
    'author': 'Silas Vasconcelos',
    'author_email': 'silasvasconcelos@hotmail.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/silasvasconcelos/doc2pdf',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
