import pytest
import os

from seeq.spy.jobs import _common


@pytest.mark.unit
def test_running_in_datalab():
    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = ''
    assert _common.running_in_datalab() is False

    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = 'true'
    assert _common.running_in_datalab() is True


@pytest.mark.unit
def test_running_in_executor():
    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = ''
    assert _common.running_in_executor() is False

    os.environ['SEEQ_SDL_CONTAINER_IS_EXECUTOR'] = 'true'
    assert _common.running_in_executor() is True


@pytest.mark.unit
def test_label_from_executor():
    assert _common.get_label_from_executor() == ''

    os.environ['SEEQ_SDL_LABEL'] = ''
    assert _common.get_label_from_executor() == ''

    os.environ['SEEQ_SDL_LABEL'] = 'explicit'
    assert _common.get_label_from_executor() == 'explicit'
