######################################################################
#   freemobsms -- A tool to send sms notification toward a Free Mobile
#   subscriber.
#   Author: h2d2021 at protonmail.com
#   Copyright (C) 2021 h2d (pseudonym)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
######################################################################

from setuptools import setup

setup(
    name = 'freemobsms',
    version = "1.0.2",
    packages = [ 'freemobsms' ],
    author = 'h2d',
    author_email = 'h2d2021@protonmail.com',
    url = '',
    description = 'Free mobile SMS notifier.',
    long_description = """This module aim is to allow sending notifications as SMS messages.

    Note that the only targeted provider is Free Mobile and that the SMS notification option must be enabled through the subscriber interface (https://mobile.free.fr).

    Type the following command to install:
        ``pip install freemobsms``, or depending of your environment
        ``pip3 install freemobsms``, or
        ``python3 -m pip install freemobsms``

    The package can be used at the command line as a program or as a function.

    1. At the command line (if you installed the program via pip on any Unix system --
    Linux, Mac OS X):
    ``freemobsms user_id key message``
    2. from a python script by simply using this kind of code:
    ``from freemobsms import send_sms``
    ``send_sms(user_id, key, "hello world!")``


    The author of this module is not in any manner related to Free SAS.""",
    classifiers = [ 'License :: OSI Approved :: GNU Affero General Public'
                   ' License v3' ],
    install_requires = [ 'requests' ],
    scripts = [ 'freemobsms/freemobsms' ],
    license = "GNU Affero General Public License",
    package_data = {'freemobsms': ['COPYING']}
)

