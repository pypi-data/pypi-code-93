# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3stopwatch",
    packages=["k3stopwatch"],
    version="0.1.0",
    license='MIT',
    description='StopWatch - library for adding timers and tags in your code for performance monitoring',
    long_description='# k3stopwatch\n\n[![Action-CI](https://github.com/pykit3/k3stopwatch/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3stopwatch/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3stopwatch.svg?branch=master)](https://travis-ci.com/pykit3/k3stopwatch)\n[![Documentation Status](https://readthedocs.org/projects/k3stopwatch/badge/?version=stable)](https://k3stopwatch.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3stopwatch)](https://pypi.org/project/k3stopwatch)\n\nStopWatch - library for adding timers and tags in your code for performance monitoring\n\nk3stopwatch is a component of [pykit3] project: a python3 toolkit set.\n\n\nStopWatch operates on a notion of "spans" which represent scopes of code for which we\nwant to measure timing. Spans can be nested and placed inside loops for aggregation.\n\nStopWatch requires a root scope which upon completion signifies the end of the round\nof measurements. On a server, you might use a single request as your root scope.\n\nStopWatch produces two kinds of reports.\n1) Aggregated (see _reported_values).\n2) Non-aggregated or "tracing" (see _reported_traces).\n\n\n\n# Install\n\n```\npip install k3stopwatch\n```\n\n# Synopsis\n\n```python\n\nimport k3stopwatch\nsw  = k3stopwatch.StopWatch()\n\nwith sw.timer(\'rwoot\'):\n    for i in range(50):\n         with sw.timer(\'inner_task\'):\n             print("do_inner_task(i)")\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3',
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3stopwatch',
    keywords=['python', 'stopwatch'],
    python_requires='>=3.0',

    install_requires=['k3ut>=0.1.15,<0.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3'],
)
