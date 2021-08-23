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


import warnings

import qumulo.lib.request as request

from qumulo.lib.identity_util import EVERYONE_ID
from qumulo.lib.uri import UriBuilder


@request.request
def smb_list_shares_v1(conninfo, credentials):
    """
    Deprecated.  List all shares, with read_only/allow_guest_access permissions
    flags displayed (even if permissions are more complex)
    """
    method = 'GET'
    uri = '/v1/smb/shares/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def smb_list_share_v1(conninfo, credentials, id_):
    """
    Deprecated.  Get a given share, with read_only/allow_guest_access
    permissions flags displayed (even if permissions are more complex)
    """
    id_ = str(id_)

    method = 'GET'
    uri = '/v1/smb/shares/%s' % id_

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def smb_list_shares(conninfo, credentials):
    return request.rest_request(conninfo, credentials, 'GET', '/v2/smb/shares/')


@request.request
def smb_list_share(conninfo, credentials, id_=None, name=None):
    assert [id_, name].count(None) == 1

    method = 'GET'
    uri = str(UriBuilder(path='/v2/smb/shares').add_path_component(id_ or name))

    return request.rest_request(conninfo, credentials, method, uri)


# Permissions constants
NO_ACCESS = 'NONE'
READ_ACCESS = 'READ'
WRITE_ACCESS = 'WRITE'
CHANGE_PERMISSIONS_ACCESS = 'CHANGE_PERMISSIONS'
ALL_ACCESS = 'ALL'

ALLOWED_TYPE = 'ALLOWED'
DENIED_TYPE = 'DENIED'

ALLOW_ALL_USER_PERMISSIONS = [
    {'type': ALLOWED_TYPE, 'trustee': {'auth_id': EVERYONE_ID}, 'rights': [ALL_ACCESS]}
]

# Compares equal to the default ACL which allows access to all hosts.
# Note that, at least in principle, there are other equivalent ACLs which are
# equivalent but which to not compare equal, although somebody would have to go
# out of their way to create them.
ALLOW_ALL_NETWORK_PERMISSIONS = [
    {
        'type': ALLOWED_TYPE,
        # empty == all:
        'address_ranges': [],
        # Equivalent to ALL_ACCESS, which gets normalized to this by the API:
        'rights': [READ_ACCESS, WRITE_ACCESS, CHANGE_PERMISSIONS_ACCESS],
    }
]

# This is equivalent to an empty ACL, but a bit nicer of a thing to set because
# it makes the meaning and intention explicit.
DENY_ALL_NETWORK_PERMISSIONS = [
    {
        'type': DENIED_TYPE,
        # empty == all:
        'address_ranges': [],
        'rights': [ALL_ACCESS],
    }
]


@request.request
def smb_add_share(
    conninfo,
    credentials,
    share_name,
    fs_path,
    description,
    read_only=None,
    allow_guest_access=None,
    allow_fs_path_create=False,
    access_based_enumeration_enabled=False,
    default_file_create_mode=None,
    default_directory_create_mode=None,
    permissions=None,
    bytes_per_sector=None,  # deprecated, will be removed in 3.2.0
    require_encryption=None,
    network_permissions=None,
):

    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'

    if bytes_per_sector is not None:
        warnings.warn('bytes_per_sector is deprecated', DeprecationWarning)

    if permissions is None and network_permissions is None:
        # Use the old v1 API and its semantics (i.e. default full control but
        # deny guest).
        #
        # Below fields are only supported by the v2 API.
        if require_encryption is not None:
            raise ValueError('require_encryption requires permissions be specified')

        share_info = {
            'share_name': share_name,
            'fs_path': fs_path,
            'description': description,
            'read_only': bool(read_only),
            'allow_guest_access': bool(allow_guest_access),
            'access_based_enumeration_enabled': bool(access_based_enumeration_enabled),
        }

        if default_file_create_mode is not None:
            share_info['default_file_create_mode'] = default_file_create_mode

        if default_directory_create_mode is not None:
            share_info['default_directory_create_mode'] = default_directory_create_mode

        uri = str(
            UriBuilder(path='/v1/smb/shares/', rstrip_slash=False).add_query_param(
                'allow-fs-path-create', allow_fs_path_create_
            )
        )

        return request.rest_request(conninfo, credentials, 'POST', uri, body=share_info)
    else:
        # Use the new API.
        if read_only is not None:
            raise ValueError('read_only may not be specified with permissions')
        if allow_guest_access is not None:
            raise ValueError('allow_guest_access may not be specified with permissions')
        if permissions is None:
            raise ValueError('permissions is required if network_permissions is given')

        share_info = {
            'share_name': share_name,
            'fs_path': fs_path,
            'description': description,
            'permissions': permissions,
        }

        if network_permissions is not None:
            # If not specified, default is an allow-all ACL.
            share_info['network_permissions'] = network_permissions

        if access_based_enumeration_enabled is not None:
            share_info['access_based_enumeration_enabled'] = bool(
                access_based_enumeration_enabled
            )

        if default_file_create_mode is not None:
            share_info['default_file_create_mode'] = default_file_create_mode

        if default_directory_create_mode is not None:
            share_info['default_directory_create_mode'] = default_directory_create_mode

        if require_encryption is not None:
            share_info['require_encryption'] = require_encryption

        uri = str(
            UriBuilder(path='/v2/smb/shares/', rstrip_slash=False).add_query_param(
                'allow-fs-path-create', allow_fs_path_create_
            )
        )

        return request.rest_request(conninfo, credentials, 'POST', uri, body=share_info)


@request.request
def smb_modify_share(
    conninfo,
    credentials,
    id_=None,
    old_name=None,
    share_name=None,
    fs_path=None,
    description=None,
    permissions=None,
    allow_fs_path_create=False,
    access_based_enumeration_enabled=None,
    default_file_create_mode=None,
    default_directory_create_mode=None,
    bytes_per_sector=None,  # deprecated, will be removed in 3.2.0
    require_encryption=None,
    network_permissions=None,
    if_match=None,
):
    assert [id_, old_name].count(None) == 1

    if bytes_per_sector is not None:
        warnings.warn('bytes_per_sector is deprecated', DeprecationWarning)

    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'
    if_match = None if if_match is None else if_match

    method = 'PATCH'
    uri = str(
        UriBuilder(path='/v2/smb/shares/')
        .add_path_component(id_ or old_name)
        .add_query_param('allow-fs-path-create', allow_fs_path_create_)
    )

    share_info = {}
    if share_name is not None:
        share_info['share_name'] = share_name
    if fs_path is not None:
        share_info['fs_path'] = fs_path
    if description is not None:
        share_info['description'] = description
    if permissions is not None:
        share_info['permissions'] = permissions
    if access_based_enumeration_enabled is not None:
        share_info['access_based_enumeration_enabled'] = bool(
            access_based_enumeration_enabled
        )
    if default_file_create_mode is not None:
        share_info['default_file_create_mode'] = default_file_create_mode
    if default_directory_create_mode is not None:
        share_info['default_directory_create_mode'] = default_directory_create_mode
    if require_encryption is not None:
        share_info['require_encryption'] = require_encryption
    if network_permissions is not None:
        share_info['network_permissions'] = network_permissions

    return request.rest_request(
        conninfo, credentials, method, uri, body=share_info, if_match=if_match
    )


@request.request
def smb_set_share(
    conninfo,
    credentials,
    id_,
    share_name,
    fs_path,
    description,
    permissions,
    allow_fs_path_create=False,
    access_based_enumeration_enabled=None,
    default_file_create_mode=None,
    default_directory_create_mode=None,
    if_match=None,
):
    """
    Replaces all share attributes.  The result is a share identical to what
    would have been produced if the same arguments were given on creation.
    Note that this means that an unspecified optional argument will result in
    that attribute being reset to default, even if the share currently has a
    non-default value.
    """
    allow_fs_path_create_ = 'true' if allow_fs_path_create else 'false'
    id_ = id_
    share_info = {
        'id': id_,
        'share_name': share_name,
        'fs_path': fs_path,
        'description': description,
        'permissions': permissions,
    }
    if access_based_enumeration_enabled is not None:
        share_info['access_based_enumeration_enabled'] = bool(
            access_based_enumeration_enabled
        )
    if default_file_create_mode is not None:
        share_info['default_file_create_mode'] = default_file_create_mode
    if default_directory_create_mode is not None:
        share_info['default_directory_create_mode'] = default_directory_create_mode

    uri = str(
        UriBuilder(path='/v2/smb/shares/')
        .add_path_component(id_)
        .add_query_param('allow-fs-path-create', allow_fs_path_create_)
    )

    if_match = None if if_match is None else if_match
    return request.rest_request(
        conninfo, credentials, 'PUT', uri, body=share_info, if_match=if_match
    )


@request.request
def smb_delete_share(conninfo, credentials, id_=None, name=None):
    assert [id_, name].count(None) == 1

    method = 'DELETE'
    uri = str(UriBuilder(path='/v2/smb/shares').add_path_component(id_ or name))
    return request.rest_request(conninfo, credentials, method, uri)


#                _                 _   _   _
#  ___ _ __ ___ | |__     ___  ___| |_| |_(_)_ __   __ _ ___
# / __| '_ ` _ \| '_ \   / __|/ _ \ __| __| | '_ \ / _` / __|
# \__ \ | | | | | |_) |  \__ \  __/ |_| |_| | | | | (_| \__ \
# |___/_| |_| |_|_.__/___|___/\___|\__|\__|_|_| |_|\__, |___/
#                   |_____|                        |___/
#  FIGLET: smb_settings
#


def send_smb_setting_request(conninfo, credentials, method, *args):
    uri = '/v1/smb/settings'
    return request.rest_request(conninfo, credentials, method, uri, *args)


@request.request
def set_smb_settings(conninfo, credentials, setting):
    return send_smb_setting_request(conninfo, credentials, 'PUT', setting)


@request.request
def patch_smb_settings(conninfo, credentials, setting):
    return send_smb_setting_request(conninfo, credentials, 'PATCH', setting)


@request.request
def get_smb_settings(conninfo, credentials):
    return send_smb_setting_request(conninfo, credentials, 'GET')


#                            __ _ _
#   ___  _ __   ___ _ __    / _(_) | ___  ___
#  / _ \| '_ \ / _ \ '_ \  | |_| | |/ _ \/ __|
# | (_) | |_) |  __/ | | | |  _| | |  __/\__ \
#  \___/| .__/ \___|_| |_| |_| |_|_|\___||___/
#       |_|


@request.paging_request
def list_file_handles(
    conninfo, credentials, file_number=None, resolve_paths=None, limit=None, after=None
):
    method = 'GET'
    uri = UriBuilder(path='/v1/smb/files')
    if file_number is not None:
        uri.add_query_param('file_number', file_number)
    if resolve_paths is not None:
        uri.add_query_param('resolve_paths', resolve_paths)
    if limit is not None:
        uri.add_query_param('limit', limit)
    if after is not None:
        uri.add_query_param('after', after)
    uri.append_slash()

    def get_files(uri):
        return request.rest_request(conninfo, credentials, method, str(uri))

    return request.PagingIterator(uri, get_files)


@request.request
def close_smb_file(conninfo, credentials, location):
    method = 'POST'
    uri = '/v1/smb/files/close'
    # Make up a fake list of results from v1/smb/files GET, because the close
    # endpoint is designed to take a request body that is round-tripped from
    # the files endpoint.
    # Only the value of 'location' matters.
    entry = dict()
    entry['file_number'] = 0
    handle_info = dict()
    handle_info['owner'] = '0'
    handle_info['access_mask'] = ['MS_ACCESS_FILE_READ_ATTRIBUTES']
    handle_info['version'] = 0
    handle_info['location'] = location
    handle_info['num_byte_range_locks'] = 0
    entry['handle_info'] = handle_info
    handle_infos = list()
    handle_infos.append(entry)
    return request.rest_request(conninfo, credentials, method, uri, body=handle_infos)


@request.paging_request
def list_smb_sessions(conninfo, credentials, limit=None, after=None, identity=None):
    method = 'GET'
    uri = UriBuilder(path='/v1/smb/sessions')

    if limit is not None:
        uri.add_query_param('limit', limit)
    if after is not None:
        uri.add_query_param('after', after)
    if identity is not None:
        uri.add_query_param('identity', identity)
    uri.append_slash()

    def get_sessions(uri):
        return request.rest_request(conninfo, credentials, method, str(uri))

    return request.PagingIterator(uri, get_sessions)


@request.request
def close_smb_sessions(conninfo, credentials, sessions):
    method = 'POST'
    uri = '/v1/smb/sessions/close'
    return request.rest_request(conninfo, credentials, method, uri, body=sessions)
