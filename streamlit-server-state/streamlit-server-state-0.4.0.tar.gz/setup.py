# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamlit_server_state']

package_data = \
{'': ['*']}

install_requires = \
['streamlit>=0.65.0']

extras_require = \
{':python_version < "3.8"': ['typing_extensions>=3.7.4,<4.0.0']}

setup_kwargs = {
    'name': 'streamlit-server-state',
    'version': '0.4.0',
    'description': '',
    'long_description': '# streamlit-server-state\nA "server-wide" state shared across the sessions.\n\n[![Tests](https://github.com/whitphx/streamlit-server-state/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/whitphx/streamlit-server-state/actions/workflows/tests.yml?query=branch%3Amain)\n\n[![PyPI](https://img.shields.io/pypi/v/streamlit-server-state)](https://pypi.org/project/streamlit-server-state/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/streamlit-server-state)](https://pypi.org/project/streamlit-server-state/)\n[![PyPI - License](https://img.shields.io/pypi/l/streamlit-server-state)](https://pypi.org/project/streamlit-server-state/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/streamlit-server-state)](https://pypi.org/project/streamlit-server-state/)\n\n[![GitHub Sponsors](https://img.shields.io/github/sponsors/whitphx?label=Sponsor%20me%20on%20GitHub%20Sponsors&style=social)](https://github.com/sponsors/whitphx)\n\n<a href="https://www.buymeacoffee.com/whitphx" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" width="180" height="50" ></a>\n\n```python\nimport streamlit as st\n\nfrom streamlit_server_state import server_state, server_state_lock\n\nst.title("Global Counter Example")\n\nwith server_state_lock["count"]:  # Lock the "count" state for thread-safety\n    if "count" not in server_state:\n        server_state.count = 0\n\nincrement = st.button("Increment")\nif increment:\n    with server_state_lock.count:\n        server_state.count += 1\n\ndecrement = st.button("Decrement")\nif decrement:\n    with server_state_lock.count:\n        server_state.count -= 1\n\nst.write("Count = ", server_state.count)\n\n```\n\nAs above, the API is similar to [the built-in SessionState](https://blog.streamlit.io/session-state-for-streamlit/), except one major difference - a "lock" object.\nThe lock object is introduced for thread-safety because the server-state is accessed from multiple sessions, i.e. threads.\n\n## Examples\n* [`app_global_count`](./app_global_count.py): A sample app like [the official counter example for SessionState](https://blog.streamlit.io/session-state-for-streamlit/) which uses `streamlit-server-state` instead and the counter is shared among all the sessions on the server. This is a nice small example to see the usage and behavior of `streamlit-server-state`. Try to open the app in multiple browser tabs and see the counter is shared among them.\n* [`app_chat.py`](./app_chat.py): A simple chat app using `streamlit-server-state`.\n* [`app_chat_rooms.py`](./app_chat_rooms.py): A simple chat app with room separation.\n  [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/whitphx/streamlit-server-state/main/app_chat_rooms.py)\n\n## Resources\n* [New library: streamlit-server-state, a new way to share states among the sessions on the server (Streamlit Community)](https://discuss.streamlit.io/t/new-library-streamlit-server-state-a-new-way-to-share-states-among-the-sessions-on-the-server/14981)\n',
    'author': 'Yuichiro Tachibana (Tsuchiya)',
    'author_email': 't.yic.yt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/whitphx/streamlit-server-state',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
