# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rstream']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'rstream',
    'version': '0.2.1',
    'description': 'A python client for RabbitMQ Streams',
    'long_description': "# RabbitMQ Stream Python Client\n\nA Python asyncio-based client for [RabbitMQ Streams](https://github.com/rabbitmq/rabbitmq-server/tree/master/deps/rabbitmq_stream)  \n_This is a work in progress_\n\n## Install\n\n```bash\npip install rstream\n```\n\n## Quick start\n\nPublishing messages:\n\n```python\nfrom rstream import Producer, Consumer\n\nasync with Producer('localhost', username='guest', password='guest') as producer:\n    await producer.create_stream('mystream')\n\n    for i in range(100):\n        await producer.publish('mystream', f'msg: {i}'.encode())\n\n```\n\nConsuming messages:\n\n```python\nconsumer = Consumer(\n    host='localhost',\n    port=5552,\n    vhost='/',\n    username='guest',\n    password='guest',\n)\n\nloop = asyncio.get_event_loop()\nloop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(consumer.close()))\n\ndef on_message(msg):\n    print('Got message:', msg)\n\nawait consumer.start()\nawait consumer.subscribe('mystream', on_message)\nawait consumer.run()\n```\n",
    'author': 'George Fortunatov',
    'author_email': 'qweeeze@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qweeze/rstream',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
