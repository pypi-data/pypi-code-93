# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anyd']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['anyd = anyd.cli:main']}

setup_kwargs = {
    'name': 'anyd',
    'version': '0.4.1',
    'description': 'A small framework for building and using custom Unix daemons.',
    'long_description': '# Anyd\n\nAnyd is a small framework that will help you build and use *any* custom Unix *daemon* process as a server. It will suite your daemon with API accessible over sockets, so you\'ll be able to query it for runnig your code or transmit the data. Anyd provides you a client out-of-the-box, so you can start working with your daemon instantly.\n\n# How-to\n\nAnyd provides you an app to start with:\n\n```python\nfrom anyd import Appd\n```\n\nDefine the address for your daemon, for example:\n\n```python\naddress = ("localhost", 3000)\n```\n\nThe daemon process will use it to accept connections. Next, create a daemon app:\n\n```python\nappd = Appd(address)\n```\n\nOr you can set it up with authentication for client:\n\n```python\nappd = Appd(address, authkey=b"swordfish")\n```\n\nNow, define your API endpoints, using `@appd.api`:\n\n```python\n@appd.api\ndef echo(arg: str) -> str:\n    return arg\n```\n\nAdditionally, you can use built-in logger to log something specific:\n\n```python\nfrom anyd import logging\n\n@appd.api\ndef echo(arg: str) -> str:\n    logging.info(f"echoing: {arg}")\n    return arg\n```\n\nThis function is now exposed to the client as an API endpoint, and can be executed on request.\n\nYou are ready to start the deamon:\n\n```python\nappd.start()\n```\n\nThat will block the interpreter and you\'ll see the logging output of your daemon in the terminal:\n\n```\n[INFO] Listening on 127.0.0.1:3000\n```\n\nLet\'s test it from another shell!\n\nStart from importing  `ClientSession`:\n\n```python\nfrom anyd import ClientSession\n```\n\nUse it with address and authkey you used for your daemon:\n\n```python\naddress = (\'localhost\', 3000)\n\nwith ClientSession(address, authkey=b"swordfish") as client:\n    # you can pass keyword arguments to API request\n    response = client.commit("echo", arg="hello world!")\n    # or the positional ones\n    bob = client.commit("echo", "hello Bob")\n    # you can query different API endpoints per-session\n    try:\n        # Will raise NotImplementedError:\n        # we didn\'t defined \'my_func\' endpoint on the daemon.\n        # The daemon will continue working.\n        client.commit("my_func", "hello") \n    except NotImplementedError as ex:\n        print(ex) # NotImplementedError: my_func\n\nprint(response) # hello world!\nprint(bob) # hello Bob\n```\n\n## Validators\n\nOn the daemon app you may want to define sort of validation logic for some of your endpoints. In this case, you can return an exception as a response to the client. It will be pickled and raised on the client side, so your daemon will stay up and running. Consider simple example with previous endpoit:\n\n```python\ndef validate_echo(arg: Any):\n    if not isinstance(arg, str):\n        return TypeError(f"{arg}, {type(arg)}")\n    return arg\n\n@appd.api\ndef echo(arg: str) -> str:\n    return validate_echo(arg)\n```\n\nThe function `validate_echo` is not an API endpoint of our daemon, but still its accessible for the daemon to execute it locally.\n\nNow, let\'s try to query it with wrong data:\n\n```python\nwith ClientSession(address) as client:\n    try:\n        client.commit("echo", 1) # will raise TypeError\n    except TypeError as ex:\n        print(ex) # 1, <class \'int\'>\n```\n\n# Features\n\n- Get to your server\'s functionality implementation instantly\n- Don\'t bother with a low-level sockets programming\n- The client for your server comes out of the box and is ready to use\n\n# Installation\n\nInstall it by running:\n\n```\npip install anyd\n```\n\n# Contribute\n\n- Issue Tracker: [github.com/anatolio-deb/anyd/issues](http://github.com/anatolio-deb/anyd/issues)\n- Source Code: [github.com/anatolio-deb/anyd](http://github.com/anatolio-deb/anyd)\n\n# License\n\nThe project is licensed under the BSD license.\n',
    'author': 'Anatolio Nikiforidis',
    'author_email': 'nikiforova693@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/anatolio-deb/anyd',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
