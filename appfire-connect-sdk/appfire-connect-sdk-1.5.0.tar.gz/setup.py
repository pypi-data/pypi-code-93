#
#  Copyright (c) 2020 Appfire Technologies, Inc.
#  All rights reserved.
#  This software is licensed under the provisions of the "Bob Swift Atlassian Add-ons EULA"
#  (https://bobswift.atlassian.net/wiki/x/WoDXBQ) as well as under the provisions of
#  the "Standard EULA" from the "Atlassian Marketplace Terms of Use" as a "Marketplace Product"
#  (http://www.atlassian.com/licensing/marketplace/termsofuse).
#  See the LICENSE file for more details.
#

"""Setup script for appfire-connect-sdk"""

from setuptools import setup

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

# setup()
setup(
    name="appfire-connect-sdk",
    version="1.5.0",
    description="SDK for creating and deploying appfire connect apps",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://bitbucket.org/appfire/ac-app-installer/src/master/",
    author="Steven Kling",
    author_email="steven.kling@appfire.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=["ac_app_installer", "ac_app_deploy"],
    include_package_data=True,
    install_requires=[
       "click", "funcy", "PyYAML", "questionary","coloredlogs", "pyngrok"
    ],
    entry_points={"console_scripts": ["create-appfire-app=ac_app_installer.install:process",
                                      "appfire=ac_app_deploy.deploy:process"]},
)
