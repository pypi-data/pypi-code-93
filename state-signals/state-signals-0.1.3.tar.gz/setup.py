# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['state_signals']
install_requires = \
['dataclasses>=0.8,<0.9', 'redis>=3.5,<4.0']

setup_kwargs = {
    'name': 'state-signals',
    'version': '0.1.3',
    'description': 'Package for easy management of state/event signal publishing, subscribing, and responding',
    'long_description': '# State/Event Signal Module\n\nAdds two new, simple-to-use objects:\n - SignalExporter      (for publishing state signals and handling subscribers + responses)\n - SignalResponder     (for receiving state signals, locking onto publishers, and publishing responses)\n\nAlso provides two dataclass specifications:\n - Signal              (state signal protocol definition)\n - Response            (response protocol definition)\n\nCombining redis pubsub features with state signal + response protocols, \nthese additions make state signal publishing, subscribing, receiving, \nand responding incredibly easy to integrate into any code.\n',
    'author': 'Mustafa Eyceoz',
    'author_email': 'meyceoz@redhat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/distributed-system-analysis/state-signals',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
