"""
## Pls-Logging

Pls-Logging is short for Python Local Server Logging, which refers to a log with a web interface.

It uses a modified version of [Oh-My-PickleDB](https://github.com/tory1103/oh-my-pickledb) JSON Manager for data storing.

## Pls-Logging is fun and powerful

```python
from plsl import Logging

log = Logging()  # Logging Object

log.info("info test")  # Info
log.warning("warning test")  # Warning
log.debug("debug test")  # Debug
log.error("error test")  # Error
```

## Easy to Install

```shell
# Using python pip
$ pip install plsl
```

```shell
# Using git
$ git clone https://github.com/tory1103/pls-logging
$ cd pls-logging
$ pip install -r requirements.txt
$ python setup.py install
```

## Contributing

You can propose a feature request opening an issue, or a pull request.

Here is a list of pls-logging contributors:

<a href="https://github.com/tory1103/pls-logging/graphs/contributors">
  <img src="https://contributors-img.web.app/image?repo=tory1103/pls-logging" />
</a>

<h3 align="right">Useful Links</h3>
<p align="right">
<a href="https://tory1103.github.io/pls-logging/">
Website<br>
</a>
<a href="https://tory1103.github.io/pls-logging/docs.html">
Documentation<br>
</a>
<a href="https://pypi.org/project/plsl">
PyPi<br>
</a>

</p>
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plsl",
    version="0.2",
    author="Adrián Toral",
    author_email="adriantoral@sertor.es",
    description="Python code logging with a server interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://tory1103.github.io/",
    project_urls={
        "Website": "https://github.com/tory1103/pls-logging",
        "Documentation": "https://tory1103.github.io/",
        "Issues": "https://github.com/tory1103/pls-logging/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: System :: Logging",
    ],
    packages=["plsl"],
    package_dir={"": "src"},
    data_files=[
        ("lib/site-packages/plsl/static", ("src/plsl/static/icon.png", "src/plsl/static/logo.png",)),
        ("lib/site-packages/plsl/templates", ("src/plsl/templates/index.html",)),
    ],
    install_requires=["oh-my-pickledb>=0.2.3.2", "Flask>=2.0.1"],
    python_requires=">=3.6",
    keywords='python, flask, gui, server, logging, python3, server-gui, localhost',
)
