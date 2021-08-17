# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aleksis', 'aleksis.apps.hjelp', 'aleksis.apps.hjelp.migrations']

package_data = \
{'': ['*'],
 'aleksis.apps.hjelp': ['locale/ar/LC_MESSAGES/*',
                        'locale/de_DE/LC_MESSAGES/*',
                        'locale/fr/LC_MESSAGES/*',
                        'locale/la/LC_MESSAGES/*',
                        'locale/nb_NO/LC_MESSAGES/*',
                        'locale/tr_TR/LC_MESSAGES/*',
                        'static/css/hjelp/*',
                        'static/js/hjelp/*',
                        'templates/hjelp/*',
                        'templates/templated_email/*']}

install_requires = \
['aleksis-core>=2.0rc,<3.0']

entry_points = \
{'aleksis.app': ['hjelp = aleksis.apps.hjelp.apps:HjelpConfig']}

setup_kwargs = {
    'name': 'aleksis-app-hjelp',
    'version': '2.0rc3',
    'description': 'AlekSIS (School Information System)\u200a—\u200aApp Hjelp (FAQ, issue reporting and support)',
    'long_description': 'AlekSIS (School Information System)\u200a—\u200aApp Hjelp (FAQ and support)\n=================================================================\n\nAlekSIS\n-------\n\nThis is an application for use with the `AlekSIS`_ platform.\n\nFeatures\n--------\n\n* Report issues\n* Frequently asked questions\n* Ask questions\n* Feedback\n\nLicence\n-------\n\n::\n\n  Copyright © 2019, 2020, 2021 Jonathan Weth <dev@jonathanweth.de>\n  Copyright © 2019, 2020, 2021 Julian Leucker <leuckeju@katharineum.de>\n  Copyright © 2019, 2020 Hangzhi Yu <yuha@katharineum.de>\n  Copyright © 2019 Frank Poetzsch-Heffter <p-h@katharineum.de>\n  Copyright © 2020 Dominik George <dominik.george@teckids.org>  \n  Copyright © 2020 Tom Teichler <tom.teichler@teckids.org>\n\n  Licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany).\n\nPlease see the LICENCE file accompanying this distribution for the\nfull licence text or on the `European Union Public Licence`_ website\nhttps://joinup.ec.europa.eu/collection/eupl/guidelines-users-and-developers\n(including all other official language versions).\n\n.. _AlekSIS: https://aleksis.org/\n.. _European Union Public Licence: https://eupl.eu/\n',
    'author': 'Julian Leucker',
    'author_email': 'leuckeju@katharineum.de',
    'maintainer': 'Jonathan Weth',
    'maintainer_email': 'dev@jonathanweth.de',
    'url': 'https://aleksis.org/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
