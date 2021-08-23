# Copyright (c) 2020 Qumulo, Inc.
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

# Copyright (c) 2020 Qumulo, Inc. All rights reserved.
#
# NOTICE: All information and intellectual property contained herein is the
# confidential property of Qumulo, Inc. Reproduction or dissemination of the
# information or intellectual property contained herein is strictly forbidden,
# unless separate prior written permission has been obtained from Qumulo, Inc.

# XXX: Please add types to the functions in this file. Static type checking in
# Python prevents bugs!
# mypy: ignore-errors


import qumulo.lib.opts
import qumulo.rest.encryption as encryption


class RotateEncryptionKeysCommand(qumulo.lib.opts.Subcommand):
    NAME = 'rotate_encryption_keys'
    SYNOPSIS = 'Rotate the at-rest encryption master keys.'

    @staticmethod
    def main(conninfo, credentials, _args):
        resp = encryption.rotate_keys(conninfo, credentials)
        assert (
            resp.data is None
        ), 'Unexpected response from key rotation API: {}'.format(resp)
        print('Key rotation complete')


class EncryptionGetStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_status'
    SYNOPSIS = 'Get at-rest encryption status.'

    @staticmethod
    def main(conninfo, credentials, _args):
        resp = encryption.status(conninfo, credentials)
        print(resp)
