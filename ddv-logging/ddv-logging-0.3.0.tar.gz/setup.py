# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ddv', 'ddv.logging']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'ddv-logging',
    'version': '0.3.0',
    'description': 'Python logging formatters, filters, and convenience methods',
    'long_description': '# DDV Logging\n\nPython logging formatters, filters, and convenience methods.\n\n**GitLab:** https://gitlab.com/davidevi/ddv-logging\n\n**PyPi:** https://pypi.org/project/ddv-logging/\n\n**Features:**\n- Can enable printing of logs to `stdout`\n- Can indent logs based on position in stack trace\n- Can colour the log level\n- Can filter out modules from the log output based on verbosity levels\n\n### Usage Example\n\nThe code:\n```python\nimport logging\n\nfrom ddv.logging import log_to_stdout\n\nlogger = logging.getLogger(__name__)\n\n\nclass A(object):\n    def __init__(self):\n        self.logger = logging.getLogger(__name__ + ".A")\n        self.logger.debug("Creating instance of A")\n        self.b = B()\n        self.A1()\n\n    def A1(self):\n        self.logger.info("A1 has been called")\n\n\nclass B(object):\n    def __init__(self):\n        self.logger = logging.getLogger(__name__ + ".B")\n        self.logger.debug("Creating instance of B")\n        self.c = C()\n        self.B1()\n\n    def B1(self):\n        self.logger.info("B1 has been called")\n\n\nclass C(object):\n    def __init__(self):\n        self.logger = logging.getLogger(__name__ + ".C")\n        self.logger.debug("Creating instance of C")\n        self.C1()\n\n    def C1(self):\n        self.logger.info("C1 has been called")\n\n\ndef main():\n\n    verbosity_filters = {  # Verbosity 0 will display none\n        1: ["__main__.A"], # Verbosity 1 will display A\n        2: ["__main__.B"], # Verbosity 2 will display A and B\n        3: ["__main__.C"]  # Verbosity 3 will display A, B, and C\n    }\n\n    log_to_stdout(\n        logging_level=logging.DEBUG,\n        enable_colours=True,\n        enable_indentation=True,\n        verbosity_filters=verbosity_filters,\n        verbosity_level=2,\n    )\n\n    logger.info("Main has been called")\n    A()\n    logger.warning("Execution complete")\n\n\nif __name__ == "__main__":\n    main()\n```\n\nThe output:\n\n![Output](https://gitlab.com/davidevi/ddv-logging/-/raw/master/docs/output.png)\n\nVerbosity levels could come from the command line:\n```\nprogram --arg1 --arg2 -vvv\n```\nWhere the number of `v` dictates the verbosity level.\n\nYou could simply use the length of `-vvv` to determine verbosity level.  \n',
    'author': 'Davide Vitelaru',
    'author_email': 'davide@vitelaru.com',
    'maintainer': 'Davide Vitelaru',
    'maintainer_email': 'davide@vitelaru.com',
    'url': 'https://gitlab.com/davidevi/ddv-logging',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
