# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['servicecatalogtordf']

package_data = \
{'': ['*']}

install_requires = \
['datacatalogtordf>=1.4.7,<2.0.0', 'skolemizer>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'servicecatalogtordf',
    'version': '0.1.0a11',
    'description': 'A library that will map a service catalog (cpsv) to rdf',
    'long_description': '![Tests](https://github.com/Informasjonsforvaltning/servicecatalogtordf/workflows/Tests/badge.svg)\n[![codecov](https://codecov.io/gh/Informasjonsforvaltning/servicecatalogtordf/branch/main/graph/badge.svg)](https://codecov.io/gh/Informasjonsforvaltning/servicecatalogtordf)\n[![PyPI](https://img.shields.io/pypi/v/servicecatalogtordf.svg)](https://pypi.org/project/servicecatalogtordf/)\n[![Read the Docs](https://readthedocs.org/projects/servicecatalogtordf/badge/)](https://servicecatalogtordf.readthedocs.io/)\n# servicecatalogtordf\nA library that will map a service catalog (cpsv) to rdf\n\nThe library contains helper classes for the following cpsv and related classes:\n - [PublicService](https://data.norge.no/specification/dcat-ap-no/#klasse-offentlig-tjeneste)\n - [PublicOrganization](https://data.norge.no/specification/dcat-ap-no/#klasse-offentlig-organisasjon)\n - [LegalResource](https://data.norge.no/specification/dcat-ap-no/#klasse-regulativ-ressurs)\n - [Rule](https://data.norge.no/specification/dcat-ap-no/#klasse-regel)\n - [Evidence](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/core-public-service-vocabulary-application-profile)\n - [Event](https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/core-public-service-vocabulary-application-profile)\n\n\n## Usage\n### Install\n```\n% pip install servicecatalogtordf\n```\n### Getting started\n```\nfrom datacatalogtordf import Catalog\nfrom servicecatalogtordf import PublicOrganization, Service\n\n# Create catalog object\ncatalog = Catalog()\ncatalog.identifier = "http://example.com/catalogs/1"\ncatalog.title = {"en": "A service catalog"}\ncatalog.publisher = "https://example.com/publishers/1"\n\n# Create a service:\nservice = Service("http://example.com/services/1")\nservice.title = {"nb": "inntektsAPI", "en": "incomeAPI"}\n# Create a public organization:\npublic_organization = PublicOrganization("https://example.com/publishers/1")\n# Add it to the service:\nservice.has_competent_authority = public_organization\n#\n# Add service to catalog:\ncatalog.services.append(service)\n\n# Get rdf representation in turtle (default)\nrdf = catalog.to_rdf()\nprint(rdf)\n```\n## Development\n### Requirements\n- [pyenv](https://github.com/pyenv/pyenv) (recommended)\n- [pipx](https://github.com/pipxproject/pipx) (recommended)\n- [poetry](https://python-poetry.org/)\n- [nox](https://nox.thea.codes/en/stable/)\n- [nox-poetry](https://github.com/cjolowicz/nox-poetry)\n\n```\n% pipx install poetry==1.1.7\n% pipx install nox==2021.06.12\n% pipx inject nox nox-poetry\n```\n### Install\n```\n% git clone https://github.com/Informasjonsforvaltning/servicecatalogtordf.git\n% cd servicecatalogtordf\n% pyenv install 3.7.11\n% pyenv install 3.8.11\n% pyenv install 3.9.6\n% pyenv local 3.7.11 3.8.11 3.9.6\n% poetry install\n```\n### Run all sessions\n```\n% nox\n```\n### Run all tests with coverage reporting\n```\n% nox -rs tests\n```\n### Debugging\nYou can enter into [Pdb](https://docs.python.org/3/library/pdb.html) by passing `--pdb` to pytest:\n```\nnox -rs tests -- --pdb\n```\nYou can set breakpoints directly in code by using the function `breakpoint()`.\n',
    'author': 'Stig B. Dørmænen',
    'author_email': 'stigbd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Informasjonsforvaltning/servicecatalogtordf',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
