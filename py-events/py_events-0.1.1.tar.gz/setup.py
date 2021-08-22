# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_events']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-events',
    'version': '0.1.1',
    'description': 'Basic event system for python',
    'long_description': '# Events\nA simple event system for using as a component in larger systems.\n\nInspired by [C# events](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/events/).\n\n## Getting Started\n\nThis library provides a mechanism to subscribe to and publish events. The primary use case is to enable code that processes events to be separated from the code that generated or detects them.\n\nOne common use case would be in implementing a statistics tracker for a game. You would not want to classes/modules responsible for managing the game logic (like a player\'s HP or calculating combat damage) to be polluted with dozens (or hundreds) or lines of counter incrementing logic (or even worse, user interface updates for those statistics). With this library you could simply fire an event from relevant places and let a dedicated statistics management module/component handle logging, saving, presenting and forwarding statistics about what happened.\n\nOrganized properly, using events can allow for a much greater separation of concerns and simplify otherwise complex logic dramatically.\n\n\n### Define your event\n\nThe core of this library is the `Event` class. The primary use of `Event` is to subclass it to define a new type of event. Typically, a subclass of `Event` only needs to override the `__init__` method to set up any new attributes that you want the event to have.\n\n\n#### Define a custom event\n```python\nfrom py_events import Event\nclass CustomEvent(Event):\n    """ My custom event. """\n\n    def __init__(self, message:str):\n        """This event contains a message to be sent to handlers."""\n\n        super().__init__()\n\n        self.message = message\n```\n\n\n### Set up a handler\n\nOnce you have an `Event` subclass defined, you can create a `subscriber` for the event. A `subscriber` is a callable that accepts the event being fired as it\'s only positional argument. Typically this is a plain function, but can be a class with a `__call__` method defined for more complex use cases.\n\nRegistering your `subscriber` can be done in two ways. For simple functions you define directly in your application\'s source code there is the `Event.handles` method you can use as a decorator to register the function automatically. If you are importing the function from somewhere, or using a callable class instead, you can call the `Event.add_handler` method to register an already constructed callable.\n\n#### Simple handler\n```python\nimport logging\n\nfrom my_module import CustomEvent\n\n@CustomEvent.handler\ndef simple_handler(event: CustomEvent) -> None:\n    """ Log the message from my custom event. """\n\n    logging.info(event.message)\n```\n\n#### Class based handler\n```python\nimport logging\n\nfrom my_module import CustomEvent\n\nclass ComplexHandler:\n    """ Log message from custom event and keep track of number of events fired. """\n\n    def __init__(self) -> None:\n        self.events_handled_count = 0\n\n    def __call__(self, event:CustomEvent) -> None:\n        """ Log message from event and increment events_handled counter. """\n\n        logging.info(event.message)\n\n        self.events_handled_count += 1\n\n# Create a constant reference that other modules could import and use to check on the counter\nCOMPLEX_HANDLER = ComplexHandler()\n\nCustomEvent.add_handler(COMPLEX_HANDLER)\n```\n\n\n### Publish your event\n\nOnce you have a `subscriber` set up you can publish events from anywhere to have them sent to all of the `subscribers` you have set up. Firing an event is as simple as constructing an instance of it and calling it\'s `fire` method.\n\n> **Useful Note**: The base `Event` class is set up to be relatively stateless, so a single instance of an `Event` can be fired multiple times.\n\n#### Fire your event\n```python\nfrom my_module import CustomEvent\n\nCustomEvent("Hello world").fire()\n```\n\n\n',
    'author': 'Jordan Cottle',
    'author_email': 'jordancottle622@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Jordan-Cottle/Events',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
