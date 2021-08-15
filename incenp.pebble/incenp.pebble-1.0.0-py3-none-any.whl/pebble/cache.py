# pebble - Passman client
# Copyright (C) 2018,2019,2020,2021 Damien Goutte-Gattat
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

import base64
import json
import os.path
import time

from incenp.pebble.util import Error
from sjcl import SJCL

_fields = ['description',
           'username',
           'password',
           'files',
           'custom_fields',
           'otp',
           'email',
           'tags',
           'url',
           'compromised']


class Vault:

    def __init__(self, server, name, basedir, key, caching=True):
        self._server = server
        self._name = name
        self._cachedir = os.path.join(basedir,
                server.host, server.user, name)
        self._datafile = os.path.join(self._cachedir, 'data')
        self._infofile = os.path.join(self._cachedir, 'info')
        self._uuidfile = os.path.join(self._cachedir, 'uuid')
        self._caching = caching

        if hasattr(key, '__call__'):
            self._get_key = key
        else:
            self._get_key = lambda: key

        self._info = None
        self._data = None
        self._cryptor = SJCL()

    def _get_info(self):
        if not self._info:
            if os.path.exists(self._infofile):
                with open(self._infofile, 'r') as f:
                    self._info = json.load(f)
            else:
                self._info = self._server.find_vault(self._name)

        return self._info

    def _needs_refresh(self, age):
        if not os.path.exists(self._datafile):
            # Always refresh if we don't have any cached data
            return True
        elif age == 0:
            # Caller explicitly requested a refresh
            return True
        elif age < 0:
            # Caller explicitly requested no refresh
            return False

        # Refresh if the cached data is too old
        mtime = os.path.getmtime(self._datafile)
        now = time.time()
        if mtime + age < now:
            return True
        else:
            return False

    def _write_cache(self):
        if not self._caching:
            return

        if not os.path.exists(self._cachedir):
            os.makedirs(self._cachedir, 0o0700)
        with open(self._infofile, 'w') as f:
            f.write(json.dumps(self._info, indent=0))
        with open(self._datafile, 'w') as f:
            f.write(json.dumps(self._data, indent=0))
            f.write('\n')
        if os.path.exists(self._uuidfile):
            os.remove(self._uuidfile)

    def _read_cache(self):
        with open(self._datafile, 'r') as f:
            self._data = json.load(f)

    def load(self, age=86400):
        if self._needs_refresh(age):
            self._data = self._server.get_vault(self._get_info()['guid'])
            self._write_cache()
        else:
            self._read_cache()

    def clear(self):
        if os.path.exists(self._infofile):
            os.remove(self._infofile)
        if os.path.exists(self._datafile):
            os.remove(self._datafile)
        if os.path.exists(self._uuidfile):
            os.remove(self._uuidfile)
        if os.path.exists(self._cachedir):
            os.rmdir(self._cachedir)

    def search(self, labels=[], decrypt=False):
        llabels = [l.lower() for l in labels]
        if len(llabels) == 0:
            creds = [cred for cred in self._data['credentials']]
        else:
            creds = []
            for cred in self._data['credentials']:
                for label in llabels:
                    if label in cred['label'].lower():
                        creds.append(cred)
                        break

        if decrypt:
            creds = [self._decrypt_entry(cred) for cred in creds]

        return creds

    def get(self, cid, decrypt=False):
        for credential in self._data['credentials']:
            if credential['credential_id'] == cid:
                if decrypt:
                    return self._decrypt_entry(credential)
                return credential
        return None

    def get_decrypted_file_data(self, file):
        return self._decrypt_field(file['file_data'])

    def get_name(self):
        return self._name

    def _decrypt_entry(self, credential):
        decrypted = {}
        for key, value in credential.items():
            if key in _fields and value:
                decrypted[key] = self._decrypt_field(value)
            else:
                decrypted[key] = value
        return decrypted

    def _encrypt_entry(self, credential):
        for field in _fields:
            credential[field] = self._encrypt_field(credential[field])

    def _decrypt_field(self, field):
        ciphertext = json.loads(base64.b64decode(field))
        try:
            plaintext = self._cryptor.decrypt(ciphertext, self._get_key())
            try:
                return json.loads(plaintext)
            except json.decoder.JSONDecodeError:
                return plaintext.decode()
        except ValueError:
            raise Error("Decryption failed: wrong passphrase or tampered data")
        except Exception as e:
            raise Error(f"Decryption failed unexpectedly: {e}")

    def _encrypt_field(self, field):
        plaintext = json.dumps(field)
        ciphertext = self._cryptor.encrypt(plaintext.encode(), self._get_key(),
                                           count=1000, dkLen=32)
        for member in ('salt', 'ct', 'iv'):
            ciphertext[member] = ciphertext[member].decode()
        return base64.b64encode(json.dumps(ciphertext).encode()).decode()

    def test_decryption(self):
        try:
            self._decrypt_field(self._get_info()['challenge_password'])
            return True
        except Error:
            return False

    def add(self, credential):
        credential['vault_id'] = self._data['vault_id']
        self._encrypt_entry(credential)
        added_credential = self._server.new_cred(credential)
        self._data['credentials'].append(added_credential)
        self._write_cache()
        return added_credential

    def update(self, credential):
        self._encrypt_entry(credential)
        updated_credential = self._server.update_cred(credential)
        for cred in self._data['credentials'][:]:
            if cred['credential_id'] == updated_credential['credential_id']:
                i = self._data['credentials'].index(cred)
                self._data['credentials'][i] = updated_credential
        self._write_cache()
        return updated_credential

    def delete(self, credential):
        deleted_credential = self._server.delete_cred(credential)
        for cred in self._data['credentials'][:]:
            if cred['credential_id'] == deleted_credential['credential_id']:
                self._data['credentials'].remove(cred)
        self._write_cache()
        return deleted_credential
