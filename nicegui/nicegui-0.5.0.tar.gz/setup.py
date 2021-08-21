# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nicegui', 'nicegui.elements']

package_data = \
{'': ['*'],
 'nicegui': ['static/*',
             'static/templates/*',
             'static/templates/css/*',
             'static/templates/highcharts/*',
             'static/templates/js/*',
             'static/templates/local/*',
             'static/templates/local/fontawesome/css/*',
             'static/templates/local/fontawesome/webfonts/*',
             'static/templates/local/ionicons/*',
             'static/templates/local/materialdesignicons/iconfont/*',
             'static/templates/local/robotofont/*',
             'static/templates/local/tailwind/*'],
 'nicegui.elements': ['lib/*']}

install_requires = \
['Pygments>=2.9.0,<3.0.0',
 'asttokens>=2.0.5,<3.0.0',
 'binding>=0.3.1,<0.4.0',
 'docutils>=0.17.1,<0.18.0',
 'justpy==0.1.5',
 'markdown2>=2.4.0,<3.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'uvicorn[watchgodreloader]>=0.14.0,<0.15.0',
 'watchgod>=0.7,<0.8',
 'websockets>=9.1,<10.0']

setup_kwargs = {
    'name': 'nicegui',
    'version': '0.5.0',
    'description': 'High-Level Abstraction Web-GUI Using Just Python',
    'long_description': '# NiceGUI\n\n<img src="https://raw.githubusercontent.com/zauberzeug/nicegui/main/sceenshots/ui-elements.png" width="300" align="right">\n\nWe like [Streamlit](https://streamlit.io/) but find it does [too much magic when it comes to state handling](https://github.com/zauberzeug/nicegui/issues/1#issuecomment-847413651).\nIn search for an alernative nice library to write simple graphical user interfaces in Python we discovered [justpy](https://justpy.io/).\nWhile too "low-level HTML" for our daily usage it provides a great basis for "NiceGUI".\n\n## Purpose\n\nNiceGUI is intended to be used for small scripts and single-page user interfaces with a very limited user base.\nLike smart home solutions, micro web apps or robotics projects.\nIt\'s also helpful for development, when tweaking/configuring a machine learning training or tuning motor controllers.\n\n## Features\n\n- browser-based graphical user interface\n- shared state between multiple browser windows\n- implicit reload on code change\n- clean set of GUI elements (label, button, checkbox, switch, slider, input, ...)\n- simple grouping with rows, columns and cards\n- general-purpose HTML and markdown elements\n- built-in timer to refresh data in intervals (even every 10 ms)\n- straight-forward data binding to write even less code\n\n## Installation\n\n```bash\npython3 -m pip install nicegui\n```\n\n## Usage\n\nWrite your nice GUI in a file `main.py`:\n\n```python\nfrom nicegui import ui\n\nui.label(\'Hello NiceGUI!\')\nui.button(\'BUTTON\', on_click=lambda: print(\'button was pressed\', flush=True))\n\nui.run()\n```\n\nLaunch it with:\n\n```bash\npython3 main.py\n```\n\nThe GUI is now avaliable through http://localhost/ in your browser.\nNote: The script will automatically reload the page when you modify the code.\n\n## Configuration\n\nYou can call `ui.run()` with optional arguments for some high-level configuration:\n\n- `host` (default: `\'0.0.0.0\'`)\n- `port` (default: `80`)\n- `title` (default: `\'NiceGUI\'`)\n- `favicon` (default: `\'favicon.ico\'`)\n- `reload`: automatically reload the ui on file changes (default: `True`)\n- `show`: automatically open the ui in a browser tab (default: `True`)\n- `interactive`: used internally when run in interactive Python shell (default: `False`)\n\n## Docker\n\nUse the [multi-arch docker image](https://hub.docker.com/repository/docker/zauberzeug/nicegui) for pain-free installation:\n\n```bash\ndocker run --rm -p 8888:80 -v $(pwd)/my_script.py:/app/main.py -it zauberzeug/nicegui:latest\n```\n\nThis will start the server at http://localhost:8888 with code from `my_script.py` within the current directory.\nCode modification triggers an automatic reload.\n\n## API\n\nThe API reference is hosted at [https://nicegui.io](https://nicegui.io) and is [implemented with NiceGUI itself](https://github.com/zauberzeug/nicegui/blob/main/main.py).\nYou should also have a look at [examples.py](https://github.com/zauberzeug/nicegui/tree/main/examples.py) for an extensive demonstration of what you can do with NiceGUI.\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zauberzeug/nicegui',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
