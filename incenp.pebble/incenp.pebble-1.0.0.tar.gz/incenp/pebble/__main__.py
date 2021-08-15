# -*- coding: utf-8 -*-
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

from configparser import ConfigParser
from enum import IntEnum
import os
import sys
import json
import datetime

import click
from click_shell import shell

from incenp.pebble import __version__
from incenp.pebble.cache import Vault
from incenp.pebble.editor import edit_credential
from incenp.pebble.server import Server
from incenp.pebble.util import SecretCache, Error

try:
    import keyring
    use_keyring = True
except:
    use_keyring = False

prog_name = "pbl"
prog_notice = f"""\
{prog_name} (Pebble {__version__})
Copyright © 2018–2021 Damien Goutte-Gattat

This program is released under the GNU General Public License.
See the COPYING file or <http://www.gnu.org/licenses/gpl.html>.
"""


def die(msg):
    print(f"{prog_name}: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_duration(s):
    n = s
    factor = 1
    if len(s) > 1 and s[-1] in ('m', 'h', 'd'):
        n = s[:-1]
        if s[-1] == 'm':
            factor = 60
        elif s[-1] == 'h':
            factor = 3600
        else:
            factor = 86400

    try:
        return int(n) * factor
    except ValueError:
        die(f"Improper duration value: {s}")


class RefreshPolicy(IntEnum):
    DEFAULT = 0,
    FORCE_REFRESH = 1,
    FORCE_NO_REFRESH = 2


class PebbleContext(object):

    def __init__(self, config_file, section='default'):
        self._config_file = config_file
        self._name = section

        self._refresh_policy = RefreshPolicy.DEFAULT
        self._config = ConfigParser()
        self._server = None
        self._vault = None
        self.tls_verify = None

        self._has_config = len(self._config.read(config_file)) > 0

        home_dir = os.getenv('HOME', default='')
        self._data_dir = '{}/pebble'.format(
            os.getenv('XDG_DATA_HOME',
                      default='{}/.local/share'.format(home_dir)))

    def reset(self, section='default', config_file=None, options=None):
        self.close()
        self._server = None
        self._vault = None
        self._vault_cache = None
        self._name = section

        if config_file:
            self._config.clear()
            self._config_file = config_file
            self._has_config = len(self._config.read(config_file)) > 0
        elif options:
            self._config.clear()
            self._config.add_section(section)
            for key, value in options.items():
                self._config.set(section, key, value)
            self._has_config = True

    def close(self):
        if self._server:
            self._server.close()

    def get_vaults(self):
        return [v['name'] for v in self.server.get_vaults()]

    def clear_password_cache(self):
        if self._vault_cache:
            self._vault_cache.reset()

    @property
    def has_config(self):
        return self._has_config

    @property
    def config(self):
        return self._config

    @property
    def config_file(self):
        return self._config_file

    @property
    def refresh_policy(self):
        return self._refresh_policy

    @refresh_policy.setter
    def refresh_policy(self, policy):
        self._refresh_policy = policy

    @property
    def server(self):
        if not self._server:
            options = self._get_server_options(self._name)
            self._server = Server(*options)
        return self._server

    @property
    def vault(self):
        if not self._vault:
            if not self._config.has_section(self._name):
                raise Error(f"No section {self._name!r} in configuration.")

            name = self._config.get(self._name, 'vault')
            caching = not(self._config.getboolean(self._name, 'nocache',
                                              fallback=False))
            max_age = self._get_max_age()
            secret = SecretCache(f"Passphrase for vault {name} on "
                                 f"{self.server.user}@{self.server.host}: ")

            vault = Vault(self.server, name, self._data_dir, secret.get_secret,
                          caching=caching)
            vault.load(max_age)

            self._vault = vault
            self._vault_cache = secret

        return self._vault

    def _get_server_options(self, section):
        if self._config.has_option(section, 'server'):
            server_section_name = self._config.get(section, 'server')
            if not self._config.has_section(server_section_name):
                raise Error(f"No server section {server_section_name!r} "
                            "in configuration file.")
            else:
                return self._get_server_options(server_section_name)
        else:
            host = self._config.get(section, 'host')
            user = self._config.get(section, 'user')
            password = None
            if self._config.has_option(section, 'password'):
                password = self._config.get(section, 'password')
            elif use_keyring:
                password = keyring.get_password(host, user)

            if password is None:
                sc = SecretCache(f"Passphrase for {user} on {host}: ",
                                 command=self._config.get(section,
                                                          'password_command',
                                                          fallback=None))
                password = sc.get_secret

            tls_verify = self.tls_verify
            if tls_verify is None:
                tls_verify = self._config.get(section, 'tls_verify',
                                              fallback='yes')
                if tls_verify in ['yes', 'on', 'enabled', 'true']:
                    tls_verify = True
                elif tls_verify in ['no', 'off', 'disabled', 'false']:
                    tls_verify = False
                elif not os.path.exists(tls_verify):
                    raise Error(f"Custom TLS CA file {tls_verify} not found.")

            return (host, user, password, tls_verify)

    def _get_max_age(self):
        if self._refresh_policy == RefreshPolicy.FORCE_REFRESH:
            return 0
        elif self._refresh_policy == RefreshPolicy.FORCE_NO_REFRESH:
            return -1
        else:
            max_age_s = self._config.get(self._name, 'max_age',
                                         fallback='86400')
            return parse_duration(max_age_s)


@shell(prompt='pbl> ',
       context_settings={'help_option_names': ['-h', '--help']})
@click.option('--config', '-c', type=click.Path(exists=False),
              default='{}/config'.format(click.get_app_dir('pebble')),
              help="Path to an alternative configuration file.")
@click.option('--section', '-s', default='default',
              help="Name of the configuration file section to use.")
@click.option('--refresh', '-f', is_flag=True, default=False,
              help="Always refresh the local cache.")
@click.option('--no-refresh', is_flag=True, default=False,
              help="Never refresh the cache even if it is old.")
@click.option('--insecure', '-k', is_flag=True, default=False,
              help="Disable verification of TLS certificates.")
@click.version_option(version=__version__, message=prog_notice)
@click.pass_context
def pebble(ctx, config, section, refresh, no_refresh, insecure):
    """Command-line client for Nextcloud’s Passman."""

    os.umask(0o0077)

    pbl = PebbleContext(config, section)
    ctx.obj = pbl

    if refresh:
        pbl.refresh_policy = RefreshPolicy.FORCE_REFRESH
    elif no_refresh:
        pbl.refresh_policy = RefreshPolicy.FORCE_NO_REFRESH

    if insecure:
        pbl.tls_verify = False

    if not pbl.has_config:
        ctx.invoke(conf)

    ctx.call_on_close(pbl.close)


@pebble.command()
@click.argument('crid', type=click.INT)
@click.pass_obj
def delete(pbl, crid):
    """Delete a credential.
    
    This command deletes the credential with the specified credential
    ID.
    """

    cred = pbl.vault.get(crid)
    if not cred:
        raise Error(f"No credential found with ID {crid}")
    answer = input(f"Really delete credential {cred['label']!r} (y/N)? ")
    if answer == 'y':
        pbl.vault.delete(cred)


@pebble.command()
@click.argument('crid', type=click.INT)
@click.option('--json', '-j', is_flag=True, default=False,
              help="Edit credential as JSON.")
@click.pass_obj
def edit(pbl, crid, json):
    """Edit an existing credential.
    
    This command allows to modify the credential with the specified
    credential ID.
    """

    cred = pbl.vault.get(crid, decrypt=True)
    if not cred:
        raise Error(f"No credential found with ID {crid}.")
    updated = edit_credential(cred, as_json=json)
    if updated:
        pbl.vault.update(updated)
    else:
        print("No changes.")


@pebble.command('list')
@click.argument('patterns', nargs=-1)
@click.option('--id', '-i', 'with_id', is_flag=True, default=False,
              help="Display credential IDs.")
@click.pass_obj
def list_credentials(pbl, patterns, with_id):
    """List credentials.
    
    This command lists the credentials matching the given pattern(s);
    if no pattern are given, all credentials are listed.
    """

    creds = pbl.vault.search(patterns)
    for cred in creds:
        if with_id:
            print(f"{cred['credential_id']}: {cred['label']}")
        else:
            print(cred['label'])


@pebble.command()
@click.option('--file', '-f', 'filename', default=None,
              help="File to save exported vault data")
@click.pass_obj
def export(pbl, filename):
    """Export vault.

    This command exports all credentials in the loaded vault into a json file.
    """

    creds = pbl.vault.search("")
    if pbl.vault.test_decryption():
        output = []
        with click.termui.progressbar(creds) as bar:
            for cred in bar:
                if cred['credential_id'] == 1:
                    continue
                decryptedCred = pbl.vault.get(cred['credential_id'], decrypt=True)
                decryptedCred.pop('vault_id', None)
                for file in decryptedCred['files']:
                    file['file_data'] = pbl.vault.get_decrypted_file_data(pbl.server.get_file(file['file_id']))
                output.append(decryptedCred)
                for custom_field in decryptedCred['custom_fields']:
                    if custom_field['field_type'] == "file":
                        custom_field['value']['file_data'] = \
                            pbl.vault.get_decrypted_file_data(pbl.server.get_file(custom_field['value']['file_id']))
        json_object = json.dumps(output, separators=(',', ':'))
        if filename is None or len(filename) < 2:
            filename_default = os.getcwd() + \
                               f"/passman-export_{pbl.vault.get_name()}_{'{:%d-%m-%Y}'.format(datetime.datetime.today())}.json"
            filename = click.termui.prompt("Path to export the decrypted vault as JSON file", filename_default)
        click.open_file(filename, 'w').write(json_object)
        click.termui.echo(f"Vault JSON export saved at {filename}")
    else:
        raise Error("Decryption failed")

@pebble.command()
@click.option('--json', '-j', is_flag=True, default=False,
              help="Edit new credential as JSON.")
@click.pass_obj
def new(pbl, json):
    """Create a new credential.
    
    This command adds a new credential to the store.
    """

    template = {
        'label': '',
        'description': '',
        'created': None,
        'changed': None,
        'tags': [],
        'email': '',
        'username': '',
        'password': '',
        'url': '',
        'favicon': '',
        'renew_interval': 0,
        'expire_time': 0,
        'delete_time': 0,
        'files': [],
        'custom_fields': [],
        'otp': {},
        'hidden': False
        }
    newcred = edit_credential(template, json)
    if newcred:
        if pbl.vault.test_decryption():
            pbl.vault.add(newcred)
    else:
        print("No changes.")


@pebble.command()
@click.pass_obj
def refresh(pbl):
    """Refresh the cache.
    
    This command refreshes the local cache from the server.
    """

    pbl.vault.load(0)


_fields = [
    ('description', 'Description', None),
    ('tags', 'Tags', lambda tags: ', '.join([tag[u'text'] for tag in tags])),
    ('url', 'URL', None),
    ('username', 'Username', None),
    ('email', 'Email', None),
    ('password', 'Password', None)
    ]


@pebble.command()
@click.argument('patterns', nargs=-1)
@click.option('--id', '-i', 'show_id', default=-1, type=click.INT,
              metavar="ID",
              help="Show the credential with the specified ID.")
@click.pass_obj
def show(pbl, patterns, show_id):
    """Show credential(s).
    
    This command shows the credentials matching the given pattern(s);
    if no pattern is given, all credentials are shown.
    """

    if show_id != -1:
        creds = [pbl.vault.get(show_id, decrypt=True)]
    else:
        creds = pbl.vault.search(patterns, decrypt=True)
    for cred in creds:
        print(f"+---- {cred['label']} ({cred['credential_id']}) -----")
        for field_name, field_label, field_format in _fields:
            if cred[field_name]:
                if field_format:
                    formatted_field = field_format(cred[field_name])
                else:
                    formatted_field = cred[field_name]
                print(f"| {field_label}: {formatted_field}")
        if cred['custom_fields']:
            for custom in cred['custom_fields']:
                print(f"| {custom['label']}: {custom['value']}")
        print("+----")


@pebble.command()
@click.option('-f', '--force', is_flag=True, default=False,
              help="Forget any previously entered passphrase")
@click.pass_obj
def verify(pbl, force):
    """Verify a vault passphrase.
    
    This command prompts from the vault's passphrase and puts it in cache.
    """
    if force:
        pbl.clear_password_cache()

    if pbl.vault.test_decryption():
        print("Vault passphrase verified")
    else:
        print("Wrong passphrase")
        pbl.clear_password_cache()


@pebble.command()
@click.pass_obj
def clear(pbl):
    """Clear the cache.
    
    This command forcefully clears the disk cache.
    """

    pbl.vault.clear()


@pebble.command()
@click.pass_obj
def conf(pbl):
    """Edit the configuration.
    
    This command configures Pebble for use with a server.
    """

    if pbl.has_config:
        click.termui.edit(filename=pbl.config_file)
        pbl.reset(config_file=pbl.config_file)
    else:
        opts = {}
        opts['host'] = click.termui.prompt("Hostname")
        opts['user'] = click.termui.prompt("Username")
        if not use_keyring or not keyring.get_password(opts['host'],
                                                       opts['user']):
            opts['password'] = click.termui.prompt("Password", hide_input=True)
        pbl.reset(options=opts)

        vaults = pbl.get_vaults()
        if len(vaults) == 1:
            vault = vaults[0]
        else:
            vault = click.termui.prompt("Vault",
                                        type=click.termui.Choice(vaults),
                                        show_choices=True)
        pbl.config.set('default', 'vault', vault)

        if use_keyring and 'password' in opts:
            keyring.set_password(opts['host'], opts['user'], opts['password'])
            # Do not write the password in the configuration file
            pbl.config.remove_option('default', 'password')

        config_dir = os.path.dirname(pbl.config_file)
        os.makedirs(config_dir, mode=0o0700, exist_ok=True)
        with open(pbl.config_file, 'w') as f:
            pbl.config.write(f)


if __name__ == '__main__':
    try:
        pebble()
    except Error as e:
        die(e)
