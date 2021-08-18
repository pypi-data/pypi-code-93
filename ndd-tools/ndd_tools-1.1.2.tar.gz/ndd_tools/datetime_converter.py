# -*- coding: utf-8 -*-
from typing import Union
from datetime import datetime
from .constants import DATETIME_FORMATS


def str_to_datetime(target: Union[str, datetime]):
    if isinstance(target, datetime):
        return target
    if isinstance(target, str):
        for datetime_format in DATETIME_FORMATS:
            try:
                return datetime.strptime(target, datetime_format)
            except Exception:
                pass
        raise LookupError('Not match any predefined datetime formats')

    raise ValueError('this function only convert string date to datetime object')
