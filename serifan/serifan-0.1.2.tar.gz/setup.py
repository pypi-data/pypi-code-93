# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['serifan']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.13.0,<4.0.0', 'requests>=2.26.0,<3.0.0']

extras_require = \
{'docs': ['sphinx-rtd-theme>=0.5.2,<0.6.0', 'sphinxcontrib-napoleon>=0.7,<0.8']}

setup_kwargs = {
    'name': 'serifan',
    'version': '0.1.2',
    'description': 'Python wrapper for the Shortboxed API',
    'long_description': '=======\nSerifan\n=======\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n\nQuick Description\n-----------------\nA python wrapper for the shortboxed.com_ API.\n\n.. _shortboxed.com: https://shortboxed.com/\n\nInstallation\n------------\n\nPyPi\n~~~~\n\n.. code:: bash\n\n  $ pip3 install --user serifan\n\nExample Usage\n-------------\n.. code-block:: python\n\n    import serifan\n\n    m = serifan.api()\n\n    # Get this weeks comic releases.\n    results = m.new_releases()\n\n    # Print the results\n    for i in results:\n        print(f"{i.title}")\n\nDocumentation\n-------------\n- `Read the project documentation <https://serifan.readthedocs.io/en/latest/>`_\n \nBugs/Requests\n-------------\n  \nPlease use the `GitHub issue tracker <https://github.com/bpepple/serifan/issues>`_ to submit bugs or request features.\n\nLicense\n-------\n\nThis project is licensed under the `GPLv3 License <LICENSE>`_.\n',
    'author': 'Brian Pepple',
    'author_email': 'bdpepple@gmail.com',
    'maintainer': 'Brian Pepple',
    'maintainer_email': 'bdpepple@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
