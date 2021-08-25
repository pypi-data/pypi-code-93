# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['django_sysinfo', 'django_sysinfo.templatetags']

package_data = \
{'': ['*'], 'django_sysinfo': ['static/sysinfo/*', 'templates/admin/sysinfo/*']}

install_requires = \
['psutil', 'python-dateutil', 'pytz']

setup_kwargs = {
    'name': 'django-sysinfo',
    'version': '2.5.1',
    'description': 'Simple django app to expose system infos: libraries version, databae server infos...',
    'long_description': "==============\ndjango-sysinfo\n==============\n\n.. image:: https://badge.fury.io/py/django-sysinfo.png\n    :target: https://badge.fury.io/py/django-sysinfo\n\n.. image:: https://travis-ci.org/saxix/django-sysinfo.png?branch=master\n    :target: https://travis-ci.org/saxix/django-sysinfo\n\nSimple django app to expose system infos like libraries version, database server.\n\nEasy to extend to add custom checks.\n\nFeatures\n--------\n\n    - dump system informations\n    - admin integration\n    - API to add custom checks\n    - simple echo\n    - retrieve library version\n\n\nQuickstart\n----------\n\nInstall django-sysinfo::\n\n    pip install django-sysinfo\n\nput it in your `INSTALLED_APPS`::\n\n    INSTALLED_APPS=[...\n     'django_sysinfo'\n    ]\n\nadd relevant entries in your url.conf::\n\n    urlpatterns = (\n        ....\n        url(r'', include(django_sysinfo.urls)),\n    )\n\nor customize them::\n\n    from django_sysinfo.views import http_basic_login, sysinfo\n\n    urlpatterns = (\n        url('sys/info/$', http_basic_login(sysinfo), name='sys-info'),\n        url('sys/version/(?P<name>.*)/$', version, name='sys-version')\n    )\n\n\nKnown issues and limitations\n----------------------------\n\nThere are some limitations in the metrics returned by sysinfo, anyway this package is\nnot intended to be used as host/resources monitoring tool.\n\n    - Disk space returns device info, any soft limits are ignored\n    - Memory can be wrong in some virtual environments\n\n\nLinks\n~~~~~\n\n+--------------------+----------------+--------------+------------------------+\n| Stable             | |master-build| | |master-cov| |                        |\n+--------------------+----------------+--------------+------------------------+\n| Development        | |dev-build|    | |dev-cov|    |                        |\n+--------------------+----------------+--------------+------------------------+\n| Project home page: |https://github.com/saxix/django-sysinfo                 |\n+--------------------+---------------+----------------------------------------+\n| Issue tracker:     |https://github.com/saxix/django-sysinfo/issues?sort     |\n+--------------------+---------------+----------------------------------------+\n| Download:          |http://pypi.python.org/pypi/django-sysinfo/             |\n+--------------------+---------------+----------------------------------------+\n| Documentation:     |https://django-sysinfo.readthedocs.org/en/latest/       |\n+--------------------+---------------+--------------+-------------------------+\n\n.. |master-build| image:: https://secure.travis-ci.com/saxix/django-sysinfo.png?branch=master\n                    :target: http://travis-ci.com/saxix/django-sysinfo/\n\n.. |master-cov| image:: https://codecov.io/github/saxix/django-sysinfo/coverage.svg?branch=master\n            :target: https://codecov.io/github/saxix/django-sysinfo?branch=master\n\n\n.. |dev-build| image:: https://secure.travis-ci.com/saxix/django-sysinfo.png?branch=develop\n                  :target: http://travis-ci.com/saxix/django-sysinfo/\n\n.. |dev-cov| image:: https://codecov.io/github/saxix/django-sysinfo/coverage.svg?branch=develop\n        :target: https://codecov.io/github/saxix/django-sysinfo?branch=develop\n\n",
    'author': 'sax',
    'author_email': 's.apostolico@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/saxix/django-sysinfo',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
