# -*- coding: utf-8 -*-
# pebble - Passman client
# Copyright (C) 2019,2021 Damien Goutte-Gattat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from getpass import getpass
from subprocess import check_output, CalledProcessError
from shlex import split


class Error(Exception):
    pass


class SecretCache(object):

    def __init__(self, prompt, command=None):
        self._prompt = prompt
        self._command = command
        self._secret = None

    def get_secret(self):
        if not self._secret:
            if self._command:
                args = split(self._command)
                try:
                    self._secret = check_output(args).decode().rstrip()
                except CalledProcessError:
                    self._secret = getpass(self._prompt)
            else:
                self._secret = getpass(self._prompt)
        return self._secret

    def reset(self):
        self._secret = None
