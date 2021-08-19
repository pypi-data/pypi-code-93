import urllib.request

from setuptools import setup

readme = """# Vema

Vema is a solution for developing static web pages, from Python + Flask, which has the basic tools and already configured to focus on the design of the pages.

## Features

* Render pages made in HTML or MD.
* Build static pages, so you only have to upload them to your hosting.
* Seo optimization.
* Routes generator.
* Optimization of the resources of your pages.
* Free and open-source software

What feature do you miss or would you like to have?

## Install

Clone the repository and work with it. Or you can also install it as a package and develop it on your own. <https://pypi.org/project/vema/>

To install it.

```python
pip install vema
```

## Documentation

Here you can find the [project documentation](https://github.com/episuarez/vema/wiki)

## First steps

You can see the first steps here. [First steps](https://github.com/episuarez/vema/wiki#how-to-start)
""";

setup(
    name="vema",
    version="0.1.4",
    description="Vema is a solution for developing static web pages, from Python + Flask, which has the basic tools and already configured to focus on the design of the pages.",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="BSD",
    platforms='any',
    author="Epifanio Suárez Martínez",
    author_email="episuarez@pm.es",
    url="https://github.com/episuarez/vema",
    packages=["vema", "vema/src", "vema/src/exceptions"],
    install_requires=["Flask", "Frozen-Flask", "argparse"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
);
