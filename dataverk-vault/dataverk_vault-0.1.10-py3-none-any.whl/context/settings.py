import os
from collections.abc import Mapping
from pathlib import Path
from dataverk_vault.exceptions.exceptions import RequiredEnvNotSet


def read_environment_settings() -> Mapping:
    return {
        "token": get_token(),
        "app_name": get_app_name(),
        "vault_address": get_vault_address(),
        "namespace": get_namespace(),
        "auth_url": get_auth_url(),
        "secrets_url": get_secrets_url()
    }


def get_app_name():
    return os.getenv("APPLICATION_NAME")


def get_token():
    try:
        token_path = os.environ["K8S_SERVICEACCOUNT_PATH"]
    except KeyError:
        raise RequiredEnvNotSet("K8S_SERVICEACCOUNT_PATH env is not set")
    else:
        with Path(token_path).joinpath("token").open("r") as token_file:
            return token_file.read()


def get_vault_address():
    try:
        address = os.environ["VKS_VAULT_ADDR"]
    except KeyError:
        raise RequiredEnvNotSet("VKS_VAULT_ADDR env is not set")
    else:
        return address


def get_namespace():
    try:
        namespace_path = os.environ["K8S_SERVICEACCOUNT_PATH"]
    except KeyError:
        raise RequiredEnvNotSet("K8S_SERVICEACCOUNT_PATH env is not set")
    else:
        with Path(namespace_path).joinpath("namespace").open("r") as namespace_file:
            return namespace_file.read()


def get_auth_url():
    try:
        vault_auth_path = os.environ["VKS_AUTH_PATH"]
    except KeyError:
        raise RequiredEnvNotSet("VKS_AUTH_PATH env is not set")
    else:
        return f"{get_vault_address()}/v1/{vault_auth_path}"


def get_secrets_url():
    try:
        vault_kv_path = os.environ["VKS_KV_PATH"]
    except KeyError:
        raise RequiredEnvNotSet("VKS_KV_PATH env is not set")
    else:
        if get_app_name():
            return f"{get_vault_address()}/v1/{vault_kv_path}/{get_app_name()}/{get_namespace()}"
        else:
            return f"{get_vault_address()}/v1/{vault_kv_path}/{get_namespace()}"
