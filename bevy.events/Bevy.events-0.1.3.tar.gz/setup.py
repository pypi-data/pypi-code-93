# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['events']

package_data = \
{'': ['*']}

install_requires = \
['gully>=0.3,<0.4']

setup_kwargs = {
    'name': 'bevy.events',
    'version': '0.1.3',
    'description': 'An event dispatch framework designed to be used with the Bevy dependency injection framework.',
    'long_description': '# Bevy.Events\nBevy.Events is an events system designed to be used with the [Bevy](https://github.com/ZechCodes/Bevy) dependency injection framework. It uses [Gully](https://github.com/ZechCodes/Gully) for creating observable streams of event objects.\n\n## Installation\n```shell script\npip install bevy.events\n```\n\n**Documentation**\n\nBevy.Events is incredibly straightforward. You can use it as an annotation type on any injectable class.\n```python\n@bevy.injectable\nclass Example:\n    events: bevy.events.EventDispatch\n    ...\n```\nIt is also possible to have multiple event dispatchers in the same Bevy context by giving them names. \n```python\n@bevy.injectable\nclass Example:\n    events: bevy.events.EventDispatch["my-event-dispatch"]\n    ...\n```\nTo send an event use the `dispatch` on the event dispatch and pass it the event name to dispatch and all the args to pass to the watchers.\n```python\n@bevy.injectable\nclass Example:\n    events: bevy.events.EventDispatch\n    ...\n\n    async def recieved_message(self, message):\n        await self.dispatch("message-received", message)\n```\nTo register a watcher just call `watch` on the event dispatch and pass it an event name to `watch` for and a coroutine callback. The callback will be passed all args that were given to the `dispatch` method.\n```python\n@bevy.injectable\nclass Example:\n    events: bevy.events.EventDispatch\n    def __init__(self):\n        self.events.watch("message-received", self.on_message_received)\n    async def on_message_received(self, message):\n        ...\n```\n`watch` returns a [Gully observer](https://github.com/ZechCodes/Gully#gullyobservablegullygully) so that the event watcher can be enabled or disabled as needed.\n\nThe event dispatchers will be shared by all class instances in the Bevy context. Events dispatched on a named dispatcher will only be sent to watchers of that event dispatcher. Any class in the context can access the same same event dispatcher just by giving the annotation the same name.\n',
    'author': 'Zech Zimmerman',
    'author_email': 'hi@zech.codes',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ZechCodes/Bevy/bevy/events/README.md',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
