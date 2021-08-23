import pytest

from tests.core.users.factories import UserFactory


@pytest.fixture
def user():
    return UserFactory()
