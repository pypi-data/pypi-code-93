import tempfile

import pytest
from koalak.databases import ListTxtDatabase


def test_simple():
    with tempfile.NamedTemporaryFile() as f:
        db = ListTxtDatabase(f.name)
        assert len(db) == 0
        assert db.count() == 0

        db.insert("a")
        assert len(db) == 1
        assert db.count() == 1
        assert db.list() == ["a"]

        db.insert("b")
        assert len(db) == 2
        assert db.count() == 2
        assert db.list() == ["a", "b"]

        db.remove("a")
        assert len(db) == 1
        assert db.count() == 1
        assert db.list() == ["b"]


def test_remove():
    with tempfile.NamedTemporaryFile() as f:
        db = ListTxtDatabase(f.name)
        db.insert("a")
        db.insert("b")
        db.insert("c")

        assert db.list() == ["a", "b", "c"]

        db.remove("c")
        assert db.list() == ["a", "b"]


def test_remove_not_found():
    with tempfile.NamedTemporaryFile() as f:
        db = ListTxtDatabase(f.name)
        db.insert("a")

        with pytest.raises(TypeError):
            db.remove("b")


def test_contain():
    with tempfile.NamedTemporaryFile() as f:
        db = ListTxtDatabase(f.name)
        assert "a" not in db
        assert "b" not in db

        db.insert("a")
        assert "a" in db

        db.insert("b")
        assert "a" in db
        assert "b" in db
        assert "c" not in db

        db.insert("c")
        assert "a" in db
        assert "b" in db
        assert "c" in db

        db.remove("a")
        assert "a" not in db


def test_unique():
    with tempfile.NamedTemporaryFile() as f:
        db = ListTxtDatabase(f.name, unique=True)
        db.insert("a")
        db.insert("b")
        db.insert("c")

        assert db.list() == ["a", "b", "c"]

        db.remove("c")
        assert db.list() == ["a", "b"]

        with pytest.raises(TypeError):
            db.insert("a")


def test_unique_function():
    with tempfile.NamedTemporaryFile() as f:
        db = ListTxtDatabase(f.name, unique=lambda x: x.split("=")[0])
        db.insert("a=1")
        db.insert("b=2")
        db.insert("c=3")

        assert db.list() == ["a=1", "b=2", "c=3"]

        with pytest.raises(TypeError):
            db.insert("a=5")
