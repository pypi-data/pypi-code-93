# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# XXX: Please add types to the functions in this file. Static type checking in
# Python prevents bugs!
# mypy: ignore-errors


import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.auth as auth

from qumulo.commands import auth as auth_commands
from qumulo.lib.opts import str_decode
from qumulo.lib.request import RequestError


class LoginCommand(qumulo.lib.opts.Subcommand):
    NAME = 'login'
    SYNOPSIS = 'Log in to qfsd to get REST credentials'

    @staticmethod
    def options(parser):
        parser.add_argument(
            '-u',
            '--username',
            type=str_decode,
            default=None,
            required=True,
            help='User name',
        )
        parser.add_argument(
            '-p',
            '--password',
            type=str_decode,
            default=None,
            help='Password (insecure, visible via ps)',
        )

    @staticmethod
    def main(conninfo, credentials, args):
        if args.password is None:
            password = qumulo.lib.opts.read_password(prompt='Password: ')
        else:
            password = args.password

        login_resp, _ = auth.login(conninfo, credentials, args.username, password)
        qumulo.lib.auth.set_credentials(login_resp, args.credentials_store)


class LogoutCommand(qumulo.lib.opts.Subcommand):
    NAME = 'logout'
    SYNOPSIS = 'Remove qfsd REST credentials'

    @staticmethod
    def options(parser):
        pass

    @staticmethod
    def main(_conninfo, _credentials, args):
        qumulo.lib.auth.remove_credentials_store(args.credentials_store)


class WhoAmICommand(qumulo.lib.opts.Subcommand):
    NAME = 'who_am_i'
    SYNOPSIS = 'Get information on the current user'

    @staticmethod
    def main(conninfo, credentials, _args):
        me = auth.who_am_i(conninfo, credentials)
        print(str(me))

        try:
            group_info_msg, related_info_msg = WhoAmICommand.get_related_info(
                conninfo, credentials, me.lookup('id')
            )
            print(str(group_info_msg))
            print(str(related_info_msg))
        except RequestError as ex:
            # Users without the ability to expand identities can't get their
            # related info. Since that information was never really core to
            # `who_am_i`, and erroring would be weird, we swallow the exception.
            if ex.status_code != 403:
                raise

    @staticmethod
    def get_related_info(conninfo, credentials, user_id):
        # Get all related group info
        try:
            group_info_msg = auth_commands.get_user_group_info_msg(
                conninfo, credentials, user_id
            )
        except RequestError as ex:
            if ex.status_code == 404:
                # Expected for an AD user, for example.
                group_info_msg = 'Not a local user.'
            else:
                raise

        # Get all related IDs
        related_info_msg = auth_commands.get_expanded_identity_information_for_user(
            conninfo, credentials, user_id
        )

        return group_info_msg, related_info_msg
