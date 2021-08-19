#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille<john@ews-network.net>

"""Top-level package for AWS CFN Custom resource Resolve parser."""

import base64
import json
import re

from boto3.session import Session
from botocore.exceptions import ClientError

__author__ = """John Preston"""
__email__ = "john@ews-network.net"
__version__ = "0.2.0"


SECRET_ARN_REGEXP = re.compile(
    r"(?:{{resolve:secretsmanager:)"
    r"(?P<arn>arn:(?P<partition>aws(?:-[a-z]+)?):secretsmanager:(?P<region>[a-z0-9-]+):"
    r"(?P<account_id>\d{12}):"
    r"(?:secret:(?P<secret_id>[a-z0-9A-Z-_./]+)))"
    r"(?P<extra>(?::SecretString:(?P<secret_key>[a-z0-9A-Z-_./]+))(?::(?P<version>[a-z0-9A-Z-]+)?)?)?(?:}})"
)

SECRET_NAME_REGEXP = re.compile(
    r"(?:{{resolve:secretsmanager:)(?P<name>[a-z0-9A-Z-_./]+)"
    r"(?P<extra>(?::SecretString:(?P<secret_key>[a-z0-9A-Z-_./]+))(?:(::)(?P<version>[a-z0-9A-Z-]+)?)?)?(?:}})"
)


def keyisset(key, obj):
    """
    Function to verify the key is present and contains something in the object

    :param str key:
    :param dict obj:
    :rtype: bool
    """
    if obj and isinstance(obj, dict) and key in obj.keys() and obj[key]:
        return True
    return False


def keypresent(key, obj):
    """
    Function to verify the key is present in the object

    :param str key:
    :param dict obj:
    :rtype: bool
    """
    if obj and isinstance(obj, dict) and key in obj.keys():
        return True
    return False


def parse_secret_resolve_string(resolve_str):
    """
    Function to parse the resolve string and return the parts of it of interest

    :param str resolve_str:
    :return: tuple of the secret, key and stage.
    :rtype: tuple
    """
    secret = None
    key = None
    stage = None
    if SECRET_ARN_REGEXP.match(resolve_str):
        parts = SECRET_ARN_REGEXP.match(resolve_str)
        secret = parts.group("arn")
        if not secret:
            raise ValueError("Unable to find the secret ARN in", resolve_str)
        key = parts.group("secret_key")
        stage = parts.group("version")
    elif SECRET_NAME_REGEXP.match(resolve_str):
        parts = SECRET_NAME_REGEXP.match(resolve_str)
        secret = parts.group("name")
    else:
        raise ValueError(
            "Unable to define secret ARN nor secret name from", resolve_str
        )
    if parts:
        key = parts.group("secret_key")
        stage = parts.group("version")

    return secret, key, stage


def retrieve_secret(secret, key=None, stage=None, client=None, session=None):
    """
    Function to retrieve the secret. If key is provided, attempts to return only the key value.
    If stage is provided, retrieves the secret for given stage.

    :param str secret:
    :param str key:
    :param str stage:
    :param boto3.client client:
    :param boto3.session.Session session:
    :return: The secret string or specific key of
    :raises: KeyError  if the key is provided but not present in secret
    :raises: ClientError in case of an error with boto3
    :raises: ResourceNotFoundException,ResourceNotFoundException if specific issue with secret retrieval
    """
    if not client and session:
        client = session.client("secretsmanager")
    elif not client and not session:
        client = Session().client("secretsmanager")
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret, VersionStage="AWSCURRENT" if not stage else stage
        )
        if keyisset("SecretString", get_secret_value_response):
            res = json.loads(get_secret_value_response["SecretString"])
        else:
            res = json.loads(
                base64.b64decode(get_secret_value_response["SecretBinary"])
            )
        if key and keypresent(key, res):
            return res[key]
        elif key and not keypresent(key, res):
            raise KeyError(f"Secret {secret} does not have a key {key}")
        return res
    except client.exceptions as error:
        print(error)
        raise
    except ClientError as error:
        print(error)
        raise


def handle(resolve_str):
    """
    Main function.

    :param resolve_str:
    :return:
    """
    parts = parse_secret_resolve_string(resolve_str)
    secret = retrieve_secret(parts[0], parts[1], parts[2])
    return secret
