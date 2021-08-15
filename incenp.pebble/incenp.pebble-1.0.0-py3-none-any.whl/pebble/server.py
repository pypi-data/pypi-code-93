# pebble - Passman client
# Copyright (C) 2018,2019,2020 Damien Goutte-Gattat
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

import requests
from requests.packages import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from incenp.pebble.util import Error


class Server:

    def __init__(self, host, user, password, tls_verify):
        self.host = host
        self.user = user
        self.tls_verify = tls_verify
        if hasattr(password, '__call__'):
            self._get_password = password
        else:
            self._get_password = lambda: password
        self._session = None

    def _do_request(self, endpoint, verb='GET', payload=None):
        if not self._session:
            if not self.tls_verify:
                urllib3.disable_warnings(InsecureRequestWarning)
            self._session = requests.Session()
            self._session.auth = (self.user, self._get_password())
        url = f'https://{self.host}/index.php/apps/passman/api/v2/{endpoint}'
        try:
            response = self._session.request(verb, url, json=payload,
                                             timeout=5, verify=self.tls_verify)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise Error(f"Cannot connect to {self.host}")
        except requests.exceptions.HTTPError:
            raise Error(f"HTTP error when communicating with {self.host}")
        except requests.exceptions.ConnectTimeout:
            raise Error(f"Timeout when connecting to {self.host}")
        except requests.exceptions.ReadTimeout:
            raise Error(f"Timeout when communicating with {self.host}")

    def close(self):
        if self._session:
            self._session.close()

    def get_vaults(self):
        return self._do_request('vaults')

    def get_vault(self, guid):
        return self._do_request(f'vaults/{guid}')

    def find_vault(self, name):
        vaults = self.get_vaults()
        for v in vaults:
            if v['name'] == name:
                return v

        return None

    def new_cred(self, cred):
        return self._do_request('credentials', verb='POST', payload=cred)

    def update_cred(self, cred):
        endpoint = f'credentials/{cred["guid"]}'
        return self._do_request(endpoint, verb='PATCH', payload=cred)

    def delete_cred(self, cred):
        endpoint = f'credentials/{cred["guid"]}'
        return self._do_request(endpoint, verb='DELETE')

    def get_file(self, file_id):
        return self._do_request(f'file/{file_id}')
