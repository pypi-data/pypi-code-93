# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.


class NoFileException(Exception):
    """Document has not got file entry"""


class ProtectedFieldException(Exception):
    """Try to update protected field"""


class NoneValueException(Exception):
    """The value equals None"""


class NotLatestException(Exception):
    """Document type is not latest"""
