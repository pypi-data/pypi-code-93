# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['globus_automate_client', 'globus_automate_client.cli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'globus-sdk>=2.0,<3.0',
 'graphviz>=0.12,<0.13',
 'jsonschema>=3.2.0,<4.0.0',
 'rich>=9.12.2,<10.0.0',
 'typer[all]>=0.3.0,<0.4.0']

entry_points = \
{'console_scripts': ['globus-automate = globus_automate_client.cli.main:app']}

setup_kwargs = {
    'name': 'globus-automate-client',
    'version': '0.12.0',
    'description': 'Client for the Globus Flows service',
    'long_description': 'Globus Automate Client\n======================\n\nThis SDK provides a CLI and a convenient Pythonic interface to the Globus\nAutomate suite of services.\n\nBasic Usage\n-----------\n\nInstall with ``pip install globus-automate-client``\n\nYou can then import Globus Automate client classes and other helpers from\n``globus_automate_client``. For example:\n\n.. code-block:: python\n\n    from globus_automate_client import create_action_client\n\n    ac = create_action_client("https://actions.globus.org/hello_world")\n\n    # Launch an Action and check its results\n    resp = ac.run({"echo_string": "Hello from SDK"})\n    assert resp.data["status"] == "SUCCEEDED"\n    print(resp.data)\n\nYou can also use the CLI interface to interact with Automate services. For\nexample:\n\n.. code-block:: BASH\n\n    globus-automate action introspect --action-url https://actions.globus.org/hello_world\n\nTesting, Development, and Contributing\n--------------------------------------\n\nGo to the\n`CONTRIBUTING <https://github.com/globus/globus-automate-client/blob/master/CONTRIBUTING.adoc>`_\nguide for detail.\n\nLinks\n-----\n| Full Documentation: https://globus-automate-client.readthedocs.io\n| Source Code: https://github.com/globus/globus-automate-client\n| Release History + Changelog: https://github.com/globus/globus-automate-client/releases\n',
    'author': 'Uriel Mandujano',
    'author_email': 'uriel@globus.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
