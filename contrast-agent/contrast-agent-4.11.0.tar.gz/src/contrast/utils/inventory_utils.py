# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.api.dtm_pb2 import ArchitectureComponent


def append_db(activity, db_info):
    """
    Add an Architecture Component to Activity
    for Teamserver to display database usage.
    """
    if not db_info or not isinstance(db_info, dict):
        return

    arch_comp = _build_architecture_component(db_info)
    activity.architectures.extend([arch_comp])


def _build_architecture_component(obj):
    """
    Builds ArchitectureComponent from dict
    """
    arch_comp = ArchitectureComponent()

    # vendor must be a string that exactly matches a value from
    # Teamserver's flowmap/technologies.json > service > one of "name"
    if "vendor" in obj and obj["vendor"]:
        arch_comp.vendor = obj["vendor"]

    if "host" in obj and obj["host"]:
        arch_comp.remote_host = obj["host"]

    if "port" in obj and obj["port"]:
        port = obj["port"]
        arch_comp.remote_port = int(port) if port else -1

    arch_comp.type = "db"

    arch_comp.url = (
        obj["database"] if "database" in obj else (arch_comp.vendor or "default")
    )

    return arch_comp
