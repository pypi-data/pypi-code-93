"""Setup"""
from setuptools import setup, find_packages
from distutils.core import setup
from codecs import open
from os import path

# Get the long description from the README file
#here = path.abspath(path.dirname(__file__))
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name="cashiersync",
    version='3.0.5',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={"": ["default_config.yaml"]},
    description="Server-side synchronization component for Cashier",
    author="Alen Siljak",
    author_email="cashier@alensiljak.eu.org",
    url="https://gitlab.com/alensiljak/cashier-sync",
    # download_url = "http://pypi.org/download/python3-chardet-1.0.1.tgz",
    keywords=["cashier", "finance", "portfolio", "ledger"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    install_requires=[
        'fastapi', 'pyyaml', 'pyxdg', 'uvicorn'
    ],
    entry_points={
        'console_scripts': [
            'cashiersync = cashiersync.main:run_server',
        ],
    },
    include_package_data=True,
    project_urls={
        "Source Code": "https://gitlab.com/alensiljak/cashier-sync.git"
    },
)
