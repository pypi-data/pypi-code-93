# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3logcollector",
    packages=["k3logcollector"],
    version="0.1.0",
    license='MIT',
    description='Scan log files on local machine, collector all interested logs, and send to somewhere for display.',
    long_description='# k3logcollector\n\n[![Action-CI](https://github.com/pykit3/k3logcollector/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3logcollector/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3logcollector.svg?branch=master)](https://travis-ci.com/pykit3/k3logcollector)\n[![Documentation Status](https://readthedocs.org/projects/k3logcollector/badge/?version=stable)](https://k3logcollector.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3logcollector)](https://pypi.org/project/k3logcollector)\n\nScan log files on local machine, collector all interested logs, and send to somewhere for display.\n\nk3logcollector is a component of [pykit3] project: a python3 toolkit set.\n\n\n#   Name\n\nlogcollector\n\nScan log files on local machine, collector all interested logs, and send\nto somewhere for display.\n\n#   Description\n\nWe may want to see all error logs on all machines, so we need to collector\nlogs, and save it in somewhere. This module is used to collector logs on one\nmachine.\n\nNormally, same error info will be loged repeatedly, we do not want\nto save duplicated log info, so logs produced by same source file at\nsame line number in one second will be combined.\n\n#   Conf\n\nconfiguration for log files. It is a dict, the key is the log name, the value\nis the configuration for the log.\n\n## file_path\n\nthe path of the log file.\n\n## is_first_line\n\nis a callback function.\nThe argument to this function is a line in log file, if the line is the\nfirst line of a log, then return `True`, otherwise return `False`.\n\n## get_level\n\nis a callback function.\nThe argument to this function is the complete log string, which may contains\nmultiple lines. It should return the level of the log, which is a string.\n\n## parse\n\nis a callback function.\nThe argument to this function is the complete log string, which may contains\nmultiple lines. It should return a dict contains following fields.\n\n-   log_ts:\n    the timestamp of this log, such as `1523936052`, is a integer.\n\n-   level:\n    the level of this log, such as \'info\'.\n\n-   source_file:\n    the source file in which the log was produced.\n\n-   line_number:\n    the number of the line at which the log was produced.\n\n## level\n\nis a list, used to specify the interested log levels.\n\n\n\n\n# Install\n\n```\npip install k3logcollector\n```\n\n# Synopsis\n\n```python\n\nimport k3logcollector\n\n\ndef send_log(log_entry):\n    print("send the log entry to database or other place.")\n\n\ndef is_first_line(line):\n    print("return True if the line is the first line of a log,")\n    print("otherwise return False.")\n\n\ndef get_level(log_str):\n    print("return the level of the log.")\n\n\ndef parse(log_str):\n    print("parse the log.")\n\n\nconf = {\n    \'front_error_log\': {\n        \'file_path\': \'path/to/log/file/xxx.error.log\',\n        \'level\': [\'warn\', \'error\'],\n        \'is_first_line\': is_first_line,\n        \'get_level\': get_level,\n        \'parse\': parse,\n    },\n}\n\nkwargs = {\n    \'node_id\': \'123abc\',\n    \'node_ip\': \'1.2.3.4\',\n    \'send_log\': send_log,\n    \'conf\': conf,\n}\n\nk3logcollector.run(**kwargs)\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3',
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3logcollector',
    keywords=['python', 'log'],
    python_requires='>=3.0',

    install_requires=['k3ut>=0.1.15,<0.2', 'k3cat<0.2,>=0.1.0', 'k3log<0.2,>=0.1.0', 'k3thread<0.2,>=0.1.0', 'k3time>=0.1.0<0.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3'],
)
