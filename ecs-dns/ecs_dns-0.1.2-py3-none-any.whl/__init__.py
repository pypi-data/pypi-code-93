# -*- coding: utf-8 -*-

"""ECS CNAME: Creates a Route 53 CNAME for ECS tasks which are assigned a public IP.."""

__author__ = """Shaun Martin"""
__email__ = "inhumantsar@protonmail.com"
__version__ = "0.1.2"

METADATA_URL = "http://169.254.170.2/v2/metadata/"

from . import models
from ._ecs_dns import (
    find_private_ips,
    find_public_dns_names,
    find_public_ips,
    create_health_check,
    create_dns_record,
)


__all__ = [
    "models",
    "METADATA_URL",
    "find_private_ips",
    "find_public_dns_names",
    "find_public_ips",
    "create_health_check",
    "create_dns_record",
]
