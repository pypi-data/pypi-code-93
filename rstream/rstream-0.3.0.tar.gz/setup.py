# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rstream']

package_data = \
{'': ['*']}

install_requires = \
['python-qpid-proton>=0.35.0,<0.36.0']

setup_kwargs = {
    'name': 'rstream',
    'version': '0.3.0',
    'description': 'A python client for RabbitMQ Streams',
    'long_description': "# RabbitMQ Stream Python Client\n\nA Python asyncio-based client for [RabbitMQ Streams](https://github.com/rabbitmq/rabbitmq-server/tree/master/deps/rabbitmq_stream)  \n_This is a work in progress_\n\n## Install\n\n```bash\npip install rstream\n```\n\n## Quick start\n\nPublishing messages:\n\n```python\nimport asyncio\nfrom rstream import Producer\n\nasync def publish():\n    async with Producer('localhost', username='guest', password='guest') as producer:\n        await producer.create_stream('mystream')\n\n        for i in range(100):\n            await producer.publish('mystream', f'msg: {i}'.encode())\n\nasyncio.run(publish())\n```\n\nConsuming messages:\n\n```python\nimport asyncio\nimport signal\nfrom rstream import Consumer\n\nasync def consume():\n    consumer = Consumer(\n        host='localhost',\n        port=5552,\n        vhost='/',\n        username='guest',\n        password='guest',\n    )\n\n    loop = asyncio.get_event_loop()\n    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(consumer.close()))\n\n    def on_message(msg):\n        print('Got message:', msg)\n\n    await consumer.start()\n    await consumer.subscribe('mystream', on_message)\n    await consumer.run()\n\nasyncio.run(consume())\n```\n\n## TODO\n\n- [ ] Documentation\n- [ ] Handle `MetadataUpdate` and reconnect to another broker on stream configuration changes\n- [ ] AsyncIterator protocol for consumer\n- [ ] Add frame size validation\n",
    'author': 'George Fortunatov',
    'author_email': 'qweeeze@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qweeze/rstream',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
