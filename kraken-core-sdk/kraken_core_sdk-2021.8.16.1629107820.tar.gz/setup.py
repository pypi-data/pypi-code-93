from setuptools import setup, find_packages
from datetime import datetime
# with open("README.md", "r") as fh:
#   long_description = fh.read()


version = datetime.now().strftime('%Y.%m.%d.%s')
setup(
    name="kraken_core_sdk",
    packages=find_packages(),
    version=version,
    description="kraken core tools",
    author="wei.fu",
    long_description='',
    long_description_content_type="text/markdown",
    author_email='mefuwei@163.com',
    url="https://github.com/kraken-cloud/kraken",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
        'loguru'
    ],

)
