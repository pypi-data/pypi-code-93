# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['time_tracker']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv>=0.12.0,<0.13.0', 'typer==0.3.2']

entry_points = \
{'console_scripts': ['tt = time_tracker.main:app']}

setup_kwargs = {
    'name': 'time-tracker',
    'version': '0.1.3',
    'description': '',
    'long_description': '# `time-tracker`\n\nTime tracker cli\n\n**Usage**:\n\n```console\n$ time-tracker [OPTIONS] COMMAND [ARGS]...\n```\n\n**Options**:\n\n* `--install-completion`: Install completion for the current shell.\n* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.\n* `--help`: Show this message and exit.\n\n**Commands**:\n\n* `log`\n* `track`: Run depending on mode\n\n## `time-tracker log`\n\n**Usage**:\n\n```console\n$ time-tracker log [OPTIONS]\n```\n\n**Options**:\n\n* `-l, --last`: Open last log file  [default: False]\n* `-o, --output`: Return log file content to terminal  [default: False]\n* `--help`: Show this message and exit.\n\n## `time-tracker track`\n\nRun depending on mode\n\n**Usage**:\n\n```console\n$ time-tracker track [OPTIONS]\n```\n\n**Options**:\n\n* `-w, --workDuration INTEGER`: Set work time (minutes)  [default: 25]\n* `-b, --breakDuration INTEGER`: Set break time (minutes)  [default: 5]\n* `-B, --bigBreakDuration INTEGER`: Set break time (minutes)  [default: 30]\n* `-m, --mode [manual|pomodoro]`: Set pomodoro mode. This will change the flow of work to 4 work sessions with small breaks and finish with a big Break  [default: pomodoro]\n* `-p, --prompt`: Set if it should prompt to go for next session  [default: True]\n* `--help`: Show this message and exit.\n',
    'author': 'Jose Cabeda',
    'author_email': 'jecabeda@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
