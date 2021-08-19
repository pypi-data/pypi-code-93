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
    'version': '0.1.2',
    'description': 'An event dispatch framework designed to be used with the Bevy dependency injection framework.',
    'long_description': '# Bevy\nBevy makes using *Dependency Injection* a breeze so that you can focus on creating amazing code.\n\n## Installation\n```shell script\npip install bevy\n```\n\n**[Documentation](docs/documentation.md)**\n\n## Dependency Injection\nPut simply, *Dependency Injection* is a design pattern where the objects that your class depends on are instantiated outside of the class. Those dependencies are then injected into your class when it is instantiated.\nThis promotes loosely coupled code where your class doesn’t require direct knowledge of what classes it depends on or how to create them. Instead your class declares what class interface it expects and an outside framework handles the work of creating the class instances with the correct interface.\n\n## Interfaces\nPython doesn’t have an actual interface implementation like many other languages. Class inheritance, however, can be used in a very similar way since sub classes will likely have the same fundamental interface as their base class. \n\n## Why Do I Care?\n*Dependency Injection* and its reliance on abstract interfaces makes your code easier to maintain:\n- Changes can be made without needing to alter implementation details in unrelated code, so long as the interface isn’t modified in a substantial way.\n- Tests can provide mock implementations of dependencies without needing to jump through hoops to inject them. They can provide the mock to the context and Bevy will make sure it is used where appropriate.\n\n## How It Works\nBevy is an object oriented *dependency injection* framework. Similar to Pydantic, it relies on Python 3\'s class\nannotations, using them to determine what dependencies a class has.\n\n**Example**\n```py\n@bevy.injectable\nclass Example:\n    dependency: Dependency\n```\nEach dependency when instantiated is added to a context repository for reuse. This allows many classes to share the same\ninstance of each dependency. This is handy for sharing things like database connections, config files, or authenticated\nAPI sessions.\n\n## Bevy Constructors\n\nTo instantiate classes and have Bevy inject their dependencies it is necessary to use a\n[`bevy.Constructor`](#Constructor). The constructor takes a [`bevy.Injectable`](#Injectable) and any args necessary to\ninstantiate it. Calling [`Constructor.build`](#Constructor.build) on the constructor will then create an instance of the\n`Injectable` with all dependencies injected.\n\n**Example**\n```py\nconstructor = bevy.Constructor(Example)\nexample = constructor.build()\n```\n### Configuring Dependencies\n\nWhen the `Constructor` encounters a dependency that is not in the context repository it will attempt to create the\ndependency. The approach is very naive, it will just call the dependency with no arguments. If it succeeds it will be\nadded to the repository for later use and injected into the class.\n\nThis behavior can be changed by passing an instantiated dependency to [`Constructor.add`](#Constructor.add).\n**Example**\n```py\nconstructor.add(Dependency("foobar"))\n```\nWhen adding an `Injectable` it is necessary to use [`Constructor.branch`](#Constructor.branch) as it will inherit all\ndependencies that are added to the constructor. Any dependencies added to the branch will not be back propagated to the\nconstructor, allowing for dependency isolation. Because branches inherit but do not propagate, their dependency\nresolution defers until `Constructor.build` is called, when it is assumed all dependencies with customized\ninstantiations have been added.\n\nBecause `Injectables` require a special lifecycle `Constructor.branch` will accept any instantiation args that should be\npassed to the class when it is constructed.\n**Example**\n```py\nbranch = constructor.branch(Dependency)\n```\n',
    'author': 'Zech Zimmerman',
    'author_email': 'hi@zech.codes',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ZechCodes/Bevy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
