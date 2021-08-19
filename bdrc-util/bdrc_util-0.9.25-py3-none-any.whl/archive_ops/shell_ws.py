"""
Callable front-end to remote web service locators
"""
import argparse
import sys
import logging

import requests
from requests import Response
import json

from util_lib.version import bdrc_util_version
from archive_ops.Resolvers import Resolvers

# These are the keys we expect back from a call to the service
# which does not specify a protocol
ENCODE_S3: str = "s3"
ENCODE_LAST_TWO: str = "last2"
ENCODE_NULL: str = "resolve_null"
# response dict key names
# When all mappings requested
RESPONSE_KEY: str = "names"
# when the default mapping is requested
DEFAULT_RESPONSE_KEY: str = "default_resolve"
ENCODE_DEFAULT = "default"

# map of Operation id to field in the return json
Resolvers_map = {
    Resolvers.DEFAULT: DEFAULT_RESPONSE_KEY,
    Resolvers.NULL: ENCODE_NULL,
    Resolvers.S3_BUCKET: ENCODE_S3,
    Resolvers.TWO: ENCODE_LAST_TWO
}

# Web service URL builders
base_url: str = "http://sattva.wal/resolve/"
default_url = base_url + "default/"


def get_mappings(root: str, archive: str, resolver: Resolvers) -> str:
    """
    Calls the service
    :param resolver:
    :param root: parent of mapped site
    :param archive: archive name
    :param resolver: path resolution strategy
    :return: resolved path
    """

    global base_url, default_url, RESPONSE_KEY, DEFAULT_RESPONSE_KEY
    mapping_result: str = ""

    # headers and args
    headers = {'Content-type': 'application/json'}
    # names is a required arg
    post_args = json.dumps(dict(names=[root, archive]))

    # set up request
    requested_api: str = base_url
    if resolver == Resolvers.DEFAULT:
        requested_api = default_url

    # noinspection PyTypeChecker
    res_response: Response = None
    try:
        res_response = requests.post(requested_api, data=post_args, headers=headers)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return ""

    call_result = res_response.status_code
    content_type = res_response.headers['content-type']
    try:
        if call_result != 200 and content_type.find('text/html') > 0:
            mapping_result = res_response.text

        if call_result == 200 and content_type.find('json') > 0:
            mapping_result = res_response.json().get(Resolvers_map[resolver])
    except Exception as e:
        logging.error(" error in ws request ", e)
        mapping_result = ""
        logging.debug(f"mapping result {mapping_result}, call_result {call_result} content_type {content_type}")

    return mapping_result


def resolve_arguments(arg_obj: object) -> Resolvers:
    """
    Modifies internal arguments - if no default resolution mapping was requested, set resolution_type
    to default
    :param arg_obj: parseargs
    :return: modified arg_obj
    """

    # if they asked for default, use it, otherwise if they didn't ask for anything else
    # return the default
    if not arg_obj.default:
        arg_obj.default = not (arg_obj.two or arg_obj.s3 or arg_obj.null)

    if arg_obj.default:
        return Resolvers.DEFAULT
    if arg_obj.two:
        return Resolvers.TWO
    if arg_obj.s3:
        return Resolvers.S3_BUCKET
    if arg_obj.null:
        return Resolvers.NULL


def locate_archive():
    parser = argparse.ArgumentParser(description="Provides mapping of archive names to paths")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-s", "--s3", action="store_true", help="Map to ENCODE_S3 storage (hexdigest[:2])")
    group.add_argument("-t", "--two", action="store_true",
                       help="Derive from last two characters of archive")
    group.add_argument("-n", "--null", action="store_true", help="No Derivation - return input as path")
    group.add_argument("-d", "--default", action="store_true", help="return Web Service default")
    parser.add_argument("root", type=str, help="parent of archive trees")
    parser.add_argument("archive", type=str, help="the name of the work")

    if "-v" in sys.argv or "--version" in sys.argv:
        print(bdrc_util_version())
        sys.exit(0)

    arg_obj: object = parser.parse_args()

    resolver: Resolvers = resolve_arguments(arg_obj)
    print(get_mappings(arg_obj.root, arg_obj.archive, resolver))


if __name__ == '__main__':
    locate_archive()
