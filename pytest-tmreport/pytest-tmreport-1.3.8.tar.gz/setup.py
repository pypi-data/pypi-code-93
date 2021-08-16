
#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys
 
setup(
    name="pytest-tmreport",
    version="1.3.8",
    author="Kevin Kai",
    author_email="zykzml7788@sina.com",
    description="this is a vue-element ui report for pytest",
    long_description=open("README.rst").read(),
    license="MIT",
    keywords="py.test pytest vue element html report",
    python_requires=">=3.6",
    url="https://pypi.org/project/pytest-tmreport/",
    packages=['pytest_tmreport'],
    install_requires=[
        "pytest"
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    include_package_data=True,
    package_data={"pytest_tmreport": ["reports/*"]},
    # the following makes a plugin available to pytest
    py_modules=['pytest_tmreport.plugin'],
    entry_points={"pytest11": ["tmreport = pytest_tmreport.plugin"]},
)
