#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
from typing import Any


def check_field_mapping(cls: Any) -> None:
    """
        1. check do->po field mapping
        2. check option field mapping
    """
    options = cls.MAPPING["options"]
    po, do = cls.MAPPING["po"], cls.MAPPING["do"]
    po_fields = set(po.__table__.columns.keys())
    do_fields = set(inspect.signature(do.__init__).parameters.keys())
    do_fields.remove("self")

    if options.get("field_mapping"):
        option_po_fields = set(options.get("field_mapping").get("po"))
        option_do_fields = set(options.get("field_mapping").get("do"))
        if len(option_po_fields) != len(option_do_fields):
            raise ValueError("Options fields must be the same.")
        if not option_po_fields.issubset(po_fields) or not option_do_fields.issubset(do_fields):
            raise ValueError("Options fields not found in po or do.")
        po_fields = po_fields - option_po_fields
        do_fields = do_fields - option_do_fields

    sys_diff = po_fields ^ do_fields
    if sys_diff:
        raise ValueError("Mapping fail, fields [{}] cant mapping.".format(sys_diff))
    return cls
