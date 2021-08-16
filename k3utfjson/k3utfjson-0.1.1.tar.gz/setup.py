# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3utfjson",
    packages=["k3utfjson"],
    version="0.1.1",
    license='MIT',
    description='force `json.dump` and `json.load` in `utf-8` encoding.',
    long_description='# k3utfjson\n\n[![Action-CI](https://github.com/pykit3/k3utfjson/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3utfjson/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3utfjson.svg?branch=master)](https://travis-ci.com/pykit3/k3utfjson)\n[![Documentation Status](https://readthedocs.org/projects/k3utfjson/badge/?version=stable)](https://k3utfjson.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3utfjson)](https://pypi.org/project/k3utfjson)\n\nforce `json.dump` and `json.load` in `utf-8` encoding.\n\nk3utfjson is a component of [pykit3] project: a python3 toolkit set.\n\n\n# Name\n\nutfjson: force `json.dump` and `json.load` in `utf-8` encoding.\n\n# Status\n\nThis library is considered production ready.\n\n\n# Install\n\n```\npip install k3utfjson\n```\n\n# Synopsis\n\n```python\n\nimport k3utfjson\n\nk3utfjson.load(\'"hello"\')\nk3utfjson.dump({})\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3',
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3utfjson',
    keywords=['python', 'json'],
    python_requires='>=3.0',

    install_requires=['k3ut<0.2,>=0.1.15'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3'],
)
