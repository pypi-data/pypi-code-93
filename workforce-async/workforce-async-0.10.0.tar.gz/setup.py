# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['workforce_async']

package_data = \
{'': ['*']}

install_requires = \
['parse>=1.0,<2.0']

setup_kwargs = {
    'name': 'workforce-async',
    'version': '0.10.0',
    'description': 'Asyncio Wrapper',
    'long_description': "# WorkForce\nAsyncio Wrapper\n\n# Install Dependencies\n> $ poetry install\n\n# Run example\n> $ poetry run python examples/http_server.py\n\n# Run tests\n> $ poetry run pytest\n\n# Interfaces\n[Snippets taken from tests](https://github.com/Kick1911/WorkForce/blob/2bf0dd7dadcefd1240bfd87df8e2aa4a32b86572/tests/test_workforce.py#L54)\n\n## Just run async functions\n```python\nworkforce = WorkForce()\n\nasync def foo():\n    await asyncio.sleep(0.8)\n    bar.count += 1\n\nf1 = workforce.schedule(foo)\n```\n\n## Just run normal functions in another thread\n```python\ndef foo():\n    bar.count += 1\n\nf = workforce.schedule(foo)\n```\n\n## Function-based tasks\n`.s()` supports both normal and async functions\n```python\nworkforce = WorkForce()\n\ndef callback(wf, task):\n    bar.result = task.result()\n\n@workforce.task(callback=callback)\nasync def add(a, b):\n    return a + b\n\ntask = add.s(4, 5)()\n\n@workforce.task()\nasync def sleep(sec):\n    await asyncio.sleep(sec)\n\nworkforce.queue('channel1')\nqueue = sleep.q(0.5)('channel1')\n```\n\n## Create queues of tasks\n```python\nworkforce = WorkForce()\nqueue = workforce.queue('channel1')\nqueue.put(foo())\nqueue.put(foo())\nqueue.put(foo())\nassert len(queue) == 3\n```\n\n## Class-based framework\nMake your own workforce that distributes workitems to Workers\n```python\nclass Company(WorkForce):\n    def get_worker(self, workitem):\n        try:\n            worker_name = {\n                'NewFeature': 'developer',\n                'Hire': 'hr',\n                'EmployeeCounseling': 'hr'\n            }[type(workitem).__name__]\n\n            return super().get_worker(worker_name)\n        except KeyError:\n            raise self.WorkerNotFound\n\ncompany = Company()\n```\n\nMake your own workers that perform tasks based on the workitem they receive\n```python\n@company.worker\nclass Developer(Worker):\n    def handle_workitem(self, workitem, *args, **kwargs):\n        callback = getattr(workitem, 'callback', None)\n\n        # All tasks here run concurrent\n        coros = (getattr(self, task_name)(workitem)\n                 for task_name in workitem.tasks)\n\n        # Hack because asyncio.gather is not recognised as a coroutine\n        async def gather(*aws, **kwargs):\n            return await asyncio.gather(*aws, **kwargs)\n\n        return gather(*coros), callback\n\n    async def design(self, workitem):\n        await asyncio.sleep(3)\n        bar.arr.append('design')\n\n    async def code(self, workitem):\n        await asyncio.sleep(2)\n        bar.arr.append('code')\n\n    async def test(self, workitem):\n        await asyncio.sleep(1)\n        bar.arr.append('test')\n\n    def make_pr(self, task, wf):\n        time.sleep(0.2)\n        bar.arr.append('make_pr')\n\ncompany.schedule_workflow(NewFeature('New trendy ML'))\n```\n\n",
    'author': 'Caswall Engelsman',
    'author_email': 'mail@cengelsman.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kick1911/WorkForce',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
