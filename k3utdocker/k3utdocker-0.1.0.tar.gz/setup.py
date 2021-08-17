# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3utdocker",
    packages=["k3utdocker"],
    version="0.1.0",
    license='MIT',
    description='unit test for python-docker',
    long_description='# k3utdocker\n\n[![Action-CI](https://github.com/pykit3/k3utdocker/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3utdocker/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3utdocker.svg?branch=master)](https://travis-ci.com/pykit3/k3utdocker)\n[![Documentation Status](https://readthedocs.org/projects/k3utdocker/badge/?version=stable)](https://k3utdocker.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3utdocker)](https://pypi.org/project/k3utdocker)\n\nunit test for python-docker\n\nk3utdocker is a component of [pykit3] project: a python3 toolkit set.\n\n\n\n\n\n\n# Install\n\n```\npip install k3utdocker\n```\n\n# Synopsis\n\n```python\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3',
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3utdocker',
    keywords=['python', 'docke'],
    python_requires='>=3.0',

    install_requires=['k3ut<0.2,>=0.1.15', 'docker>=4.5.0', 'six>=1.14.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3'],
)
