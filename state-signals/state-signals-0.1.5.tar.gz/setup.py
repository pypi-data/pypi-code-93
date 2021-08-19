# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['state_signals']
install_requires = \
['dataclasses>=0.8,<0.9', 'redis>=3.5,<4.0']

setup_kwargs = {
    'name': 'state-signals',
    'version': '0.1.5',
    'description': 'Package for easy management of state/event signal publishing, subscribing, and responding',
    'long_description': '# State/Event Signal Module\nA python package for handling state/event signals\n\nAdds two new, simple-to-use objects:\n - SignalExporter      (for publishing state signals and handling subscribers + responses)\n - SignalResponder     (for receiving state signals, locking onto publishers, and publishing responses)\n\nAlso provides two dataclass specifications:\n - Signal              (state signal protocol payload definition)\n - Response            (response protocol payload definition)\n\nCombining redis pubsub features with state signal + response protocols, \nthese additions make state signal publishing, subscribing, receiving, \nand responding incredibly easy to integrate into any python code.\n\nSee full documentation [here](https://distributed-system-analysis.github.io/state-signals/)\n\n# Installation\nThe state-signals PyPI package is available [here](https://pypi.org/project/state-signals)\n\nTo install, run `pip install state-signals`\n\n# Requirements\nThe use of this module requires the existence of an accessible redis server.\n - Redis can easily be installed with a `yum install redis` (or replace yum with package manager of choice).\n\nA redis server can be started with the `redis-server` command.\n - The default port is 6379 (also default for state-signals), but can be changed with `--port (port)`\n - A config file can also be used for greater control/detail `redis-server \\path\\to\\config`\n - Example config available [here](https://download.redis.io/redis-stable/redis.conf)\n\nSee https://redis.io/ for more details and usage\n\n# Protocol / Behaviors\n\nThe `Signal` and `Response` dataclasses define the exact fields/format of signal and response payloads.\n\nPublishing, receiving, and responding mechanisms are all detailed in `SignalExporter` and `SignalResponder` documentation. Below are details on the subscribing/awaiting protocol.\n\nAccept Subscribers and Awaiting Responses:\n - Using the `SignalExporter`, call an `exporter.initialize(legal_events, ...)`\n - Initialization will start the subscriber listener and establish legal event names\n - It will also publish an "initialization" state signal\n - Responders can then respond to the "initialization" signal to be added to the list of subs\n    - Note: A responder can subscribe at any point, unless a "shutdown" signal has been published after the initialization\n - The `SignalExporter` will now wait for (up until timeout) and read the responses of the subscribers after publishing any further signals with `exporter.publish_signal(event, ...)`\n - When finished, calling `exporter.shutdown(...)` will stop the subscriber listener, wipe the subscriber list, and publish a "shutdown" signal\n    - This signal publish will NOT listen for responses\n\nSending Responses\n - Receiving signals and sending responses can be done with the `SignalResponder`\n - To respond to a signal, simply use the `respond` method and pass in the `publisher_id` of the signal\'s publisher, and pass in the `event` being responded to.\n - (COMING SOON) `srespond(signal, ...)`: A method where the user can simply pass in the received signal object they wish to respond to instead of the signal\'s id/event\n - Responding to an "initialization" signal will subscribe the responder to that specific publisher, which will now await responses from the responder for any future signals published.\n    - NOTE: When responding to an "initialization" signal, a Response-Action-Success (RAS) code is not necessary\n    - For any future responses to that publisher\'s signals, an RAS code will be necessary, and will indicate to the publisher whether or not the responder was successful in acting upon the signal\n    - See documentation for more details on RAS codes\n\nSee the [full documentation](https://distributed-system-analysis.github.io/state-signals/) for further details, options, and more',
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
