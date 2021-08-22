#!/usr/bin/env python3
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
import requests

"""
    This module aim is to allow sending notifications as SMS messages.
    Note that the only targeted provider is Free Mobile and that the sms
    notification option must be enabled through the subscriber interface
    (https://mobile.free.fr)

    The package can be used at the command line as a program or as a function.

    1. At the command line (if you installed the program via pip on any Unix system --
    Linux, Mac OS X):
        freemobsms <user_id> <key> <message>

    2. from a python script by simply using this kind of code:
        from freemobsms import send_sms
        send_sms(user_id, key, "hello world!")

    The author of this module is not in any manner related to Free SAS.
"""

_BASE_URL = "https://smsapi.free-mobile.fr/sendmsg"

def send_sms(user, key, msg):
    """
    Sends a sms (msg) to the cell phone identified by the user and key pair.

    The user and key must be retrieved on the subscriber account at
    https://free.mobile.fr and of course the option has to be enabled.

    Args:
        user: the user id to send a message.
        key: the key to access the service for the specific user. 
        msg: the message you want to send.

    Exceptions:
        This function might raise an Exception if different scenarios with an
        associated HTTP error (the error message is anyway explicit, please 
        look the code for further details).
    """
    headers = {"User-agent":  "freemobsms client/1.0.0"}
    #data = {'user': user, 'pass': key, 'msg': msg}
    # contrary to what the official doc says, the POST method doesn't work (as
    # far as I tested)
    resp = requests.get(_BASE_URL+"?user="+user+"&pass="+key+'&msg='+msg,
                        headers=headers)#, data=data) # requests.Response
    # resp.status_code == 200 # success!
    if resp.status_code == 400:
        raise Exception("A parameter is missing, check the (user, key, msg) triplet")
    elif resp.status_code == 402:
        raise Exception("Trespassing the number of SMS limitation in time")
    elif resp.status_code == 403:
        raise Exception("Check your credentials and the service activation on mobile.free.fr")
    elif resp.status_code == 500:
        raise Exception("The server is currently unavailable, try again later")

if __name__ == "__main__":
    from sys import argv
    if len(argv) < 4:
        print("USAGE:", argv[0], "<user> <key> <msg>")
        exit(1)
    send_sms(*argv[1:4])
