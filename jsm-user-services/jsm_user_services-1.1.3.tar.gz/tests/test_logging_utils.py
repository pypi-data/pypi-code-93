from unittest import mock

import pytest

from jsm_user_services.support.local_threading_utils import add_to_local_threading
from jsm_user_services.support.local_threading_utils import remove_from_local_threading
from jsm_user_services.support.logging_utils import UserSessionIDFilter


@pytest.fixture
def session_id_filter() -> UserSessionIDFilter:
    return UserSessionIDFilter()


def test_should_set_record_session_id_to_empty_when_user_session_id_isnt_set(session_id_filter: UserSessionIDFilter):
    remove_from_local_threading("user_session_id")

    mocked_record = mock.MagicMock()

    result = session_id_filter.filter(mocked_record)

    assert result
    assert mocked_record.session_id == UserSessionIDFilter.EMPTY_FIELD


def test_should_set_record_session_id_to_user_session_id(session_id_filter: UserSessionIDFilter):
    add_to_local_threading("user_session_id", "abc")

    mocked_record = mock.MagicMock()

    result = session_id_filter.filter(mocked_record)

    assert result
    assert mocked_record.session_id == "abc"
