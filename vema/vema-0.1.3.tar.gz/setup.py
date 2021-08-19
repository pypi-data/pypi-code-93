import urllib.request

from setuptools import setup

readme = urllib.request.urlopen("https://github.com/episuarez/vema/blob/d4e18808a2b7c2b94bc6424f4a921ca621e0a4b0/readme.md").read();

setup(
    name="vema",
    version="0.1.3",
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
