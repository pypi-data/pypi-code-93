from contextlib import contextmanager
from unittest.mock import patch

from w.services.technical.yousign_service import YouSignService


def get_target(method_name):
    return YouSignService.get_patch_target(method_name)


@contextmanager
def create_success(return_value):
    with patch(get_target("create"), return_value=return_value) as m:
        yield m


@contextmanager
def create_yousign_failure():
    side_effect = RuntimeError("yousign api failed")
    with patch(get_target("create"), side_effect=side_effect) as m:
        yield m
