from unittest.mock import Mock

import pytest

from jelapi import api_connector as jelapic
from jelapi.classes import JelasticEnvGroup
from jelapi.exceptions import JelasticObjectException
from jelapi.factories import JelasticEnvGroupFactory


def test_JelasticEnvGroup_simple():
    """
    JelasticEnvGroup can be instantiated as is
    """
    JelasticEnvGroup()


def test_JelasticEnvGroup_factory():
    """
    JelasticEnvGroup can be instantiated as is
    """
    j = JelasticEnvGroupFactory()
    assert len(j.name) >= 0

    j = JelasticEnvGroupFactory(name="A")
    assert j.name == "A"
    assert j.id
    assert len(j.color) == 7


def test_JelasticEnvGroup_dict():
    """
    We can get all the envGroups
    """
    JelasticEnvGroup.dict.cache_clear()
    jelapic()._ = Mock(
        return_value={
            "array": [{"id": 1, "name": "A", "visibility": 0, "isIsolated": False}]
        },
    )

    egs = JelasticEnvGroup.dict()
    assert len(egs) == 1
    assert "A" in egs
    assert isinstance(egs["A"], JelasticEnvGroup)
    assert isinstance(egs["A"].visibility, JelasticEnvGroup.Visibility)

    # Re-fetch it, it's cached
    JelasticEnvGroup.dict()
    jelapic()._.assert_called_once()


def test_JelasticEnvGroup_get():
    """
    We can get one of the envGroups
    """
    JelasticEnvGroup.dict.cache_clear()

    jelapic()._ = Mock(
        return_value={
            "array": [{"id": 1, "name": "A", "visibility": 0, "isIsolated": False}]
        },
    )

    eg = JelasticEnvGroup.get("A")
    assert isinstance(eg, JelasticEnvGroup)
    assert isinstance(eg.visibility, JelasticEnvGroup.Visibility)

    # Re-fetch it, it's cached
    JelasticEnvGroup.get("A")
    jelapic()._.assert_called_once()

    # Now try fetching an inexistant one
    with pytest.raises(JelasticObjectException):
        JelasticEnvGroup.get("B")


def test_JelasticEnvGroup_children():
    """
    Let's check the envGroups' children
    """
    JelasticEnvGroup.dict.cache_clear()

    jelapic()._ = Mock(
        return_value={
            "array": [
                {"id": 1, "name": "A", "visibility": 0, "isIsolated": False},
                {"id": 2, "name": "A/Child-1", "visibility": 0, "isIsolated": False},
                {"id": 3, "name": "A/Child-2", "visibility": 0, "isIsolated": False},
            ]
        },
    )

    eg = JelasticEnvGroup.get("A")
    assert len(eg.children) == 2
    assert isinstance(eg.children, dict)
    assert "A/Child-1" in eg.children

    eg = JelasticEnvGroup.get("A/Child-1")
    assert len(eg.children) == 0


def test_JelasticEnvGroup_modifications():
    """
    Now let's modify these
    """
    jeg = JelasticEnvGroupFactory()
    assert jeg.is_from_api
    jeg.color = "#765432"
    assert jeg.differs_from_api()
    jelapic()._ = Mock()
    jeg.save()
    jelapic()._.assert_called_once
    assert not jeg.differs_from_api()

    jeg.visibility = JelasticEnvGroup.Visibility.SHOW_IF_NOT_EMPTY
    assert jeg.differs_from_api()
    jelapic()._ = Mock()
    jeg.save()
    jelapic()._.assert_called_once
    assert not jeg.differs_from_api()


def test_JelasticEnvGroup_creation():
    """
    Now let's create a new one
    """
    jeg = JelasticEnvGroup(name="Group-in-Test")
    assert not jeg.is_from_api
    jeg.color = "#765432"
    assert jeg.differs_from_api()
    jelapic()._ = Mock()
    jeg.save()
    jelapic()._.assert_called_once
    assert not jeg.differs_from_api()


def test_JelasticEnvGroup_deletion():
    """
    Now let's delete one from API
    """

    jeg = JelasticEnvGroupFactory()
    assert jeg.is_from_api
    jeg.delete_from_api()
    assert not jeg.is_from_api
