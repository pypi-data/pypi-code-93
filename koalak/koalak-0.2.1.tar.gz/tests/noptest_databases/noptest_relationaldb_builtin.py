from typing import List

import pytest
from koala import BaseRelationalDB

relationaldb = BaseRelationalDB


def test_relationaldbmetadata_one_cls():
    """Test the metadata of one simple class"""
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute()

    # Check class metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 1
    assert "Person" in db_metadata

    # check cls metadata
    person = db_metadata["Person"]
    assert len(person) == 1
    assert "name" in person
    assert person.exist
    assert person.cls is Person

    # check attr metadata
    name_attr = person["name"]
    assert name_attr.name == "name"
    assert name_attr.type == str
    assert name_attr.atomic_type == str
    assert name_attr.atomic_type_name == "str"
    assert not name_attr.unique
    assert not name_attr.many
    assert not name_attr.ref
    assert not name_attr.referenced_by
    assert name_attr.exist


def test_relationaldbmetadata_one_cls_many_simple_attributes():
    """Test the metadata of one simple class"""
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute()
        nickname: str = db.attribute()
        age: int = db.attribute()
        adult: bool = db.attribute()

    # Check class metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 1
    assert "Person" in db_metadata

    # check cls metadata
    person = db_metadata["Person"]
    assert person.exist
    assert len(person) == 4
    assert person.cls is Person

    for attribute_name in ["name", "nickname", "age", "adult"]:
        assert attribute_name in person

        # check attr metadata
        attribute = person[attribute_name]
        assert attribute.name == attribute_name
        assert not attribute.unique
        assert not attribute.many
        assert not attribute.ref
        assert not attribute.referenced_by
        assert attribute.exist

        if attribute_name in ["name", "nickname"]:
            assert attribute.type == str
            assert attribute.atomic_type_name == "str"
            assert attribute.atomic_type == str
        elif attribute_name == "age":
            assert attribute.type == int
            assert attribute.atomic_type == int
            assert attribute.atomic_type_name == "int"
        else:
            assert attribute.type == bool
            assert attribute.atomic_type == bool
            assert attribute.atomic_type_name == "bool"


def test_relationaldbmetadata_one_cls_with_cls_type():
    """Test the metadata of one simple class"""
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute()
        animal: "Animal" = db.attribute()

    # Check class metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 2
    assert "Person" in db_metadata

    # check cls Person metadata
    person = db_metadata["Person"]
    assert person.exist
    assert len(person) == 2
    assert "name" in person
    assert person.cls is Person

    # check attr name metadata
    name_attr = person["name"]
    assert name_attr.name == "name"
    assert name_attr.type == str
    assert name_attr.atomic_type == str
    assert name_attr.atomic_type_name == "str"
    assert not name_attr.unique
    assert not name_attr.many
    assert not name_attr.ref
    assert not name_attr.referenced_by
    assert name_attr.exist

    # check animal attribute metadata
    animal_attr = person["animal"]
    assert animal_attr.name == "animal"
    assert animal_attr.type == "Animal"
    assert animal_attr.atomic_type == "Animal"
    assert animal_attr.atomic_type_name == "Animal"
    assert not animal_attr.unique
    assert not animal_attr.many
    assert not animal_attr.ref
    assert not animal_attr.referenced_by
    assert animal_attr.exist

    # check cls Animal metadata (at this stage we don't have information about the cls)
    animal = db_metadata["Animal"]
    assert len(animal) == 0
    assert not animal.exist


def test_relationaldbmetadata_two_simple_classes():
    """Test the metadata of one simple class"""
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute()

    @db.register
    class Animal:
        name: str = db.attribute()

    # Check class metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 2
    assert "Person" in db_metadata
    assert "Animal" in db_metadata

    # check cls Person metadata
    person = db_metadata["Person"]
    assert person.exist
    assert len(person) == 1
    assert "name" in person
    assert person.cls is Person

    # check attr name metadata
    name_attr = person["name"]
    assert name_attr.name == "name"
    assert name_attr.type == str
    assert name_attr.atomic_type == str
    assert name_attr.atomic_type_name == "str"
    assert not name_attr.unique
    assert not name_attr.many
    assert not name_attr.ref
    assert not name_attr.referenced_by
    assert name_attr.exist

    # check cls Animal metadata
    animal = db_metadata["Animal"]
    assert animal.exist
    assert len(animal) == 1
    assert "name" in animal
    assert animal.cls is Animal

    # check attr name metadata
    name_attr = animal["name"]
    assert name_attr.name == "name"
    assert name_attr.type == str
    assert name_attr.atomic_type == str
    assert name_attr.atomic_type_name == "str"
    assert not name_attr.unique
    assert not name_attr.many
    assert not name_attr.ref
    assert not name_attr.referenced_by
    assert name_attr.exist


def test_relationaldbmetadata_two_classes_with_ref():
    """Test the metadata of one simple class"""
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute()
        animal: "Animal" = db.attribute(ref="owner")

    # ================================= #
    # Test metadata before second class #
    # ================================= #

    # Check DB metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 2
    assert "Person" in db_metadata
    assert "Animal" in db_metadata

    # check cls Person metadata
    person = db_metadata["Person"]
    assert person.exist
    assert len(person) == 2
    assert "name" in person
    assert "animal" in person
    assert person.cls is Person

    # check attr name metadata
    name_attr = person["name"]
    assert name_attr.name == "name"
    assert name_attr.type == str
    assert name_attr.atomic_type == str
    assert name_attr.atomic_type_name == "str"
    assert not name_attr.unique
    assert not name_attr.many
    assert not name_attr.ref
    assert not name_attr.referenced_by
    assert name_attr.exist

    # check animal attribute metadata
    animal_attr = person["animal"]
    assert animal_attr.name == "animal"
    assert animal_attr.type == "Animal"
    assert animal_attr.atomic_type == "Animal"
    assert animal_attr.atomic_type_name == "Animal"
    assert not animal_attr.unique
    assert not animal_attr.many
    assert animal_attr.ref == "owner"
    assert not animal_attr.referenced_by
    assert animal_attr.exist

    # check cls Animal metadata
    animal = db_metadata["Animal"]
    assert not animal.exist
    assert len(animal) == 1
    assert "owner" in animal
    assert animal.cls is None

    # check animal attribute metadata
    owner_attr = animal["owner"]
    assert owner_attr.name == "owner"
    # assert owner_attr.type is None
    assert owner_attr.atomic_type is Person
    assert owner_attr.atomic_type_name == "Person"
    assert not owner_attr.unique
    assert not owner_attr.many
    assert not owner_attr.ref
    assert owner_attr.referenced_by is animal_attr
    assert not owner_attr.exist

    @db.register
    class Animal:
        name: str = db.attribute()
        owner: Person = db.attribute()

    assert len(db_metadata) == 2

    # change for owner_attr
    assert owner_attr.name == "owner"
    assert owner_attr.type is Person
    assert owner_attr.atomic_type is Person
    assert owner_attr.atomic_type_name == "Person"
    assert not owner_attr.unique
    assert not owner_attr.many
    assert not owner_attr.ref
    assert owner_attr.referenced_by is animal_attr
    assert owner_attr.exist


def test_relationaldbmetadata_one_cls_empty_ref():
    """Test the metadata of one simple class referencing an attribute without the second cls"""
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute()
        animal: "Animal" = db.attribute(ref="owner")

    # Check class metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 2
    assert "Person" in db_metadata

    # check cls Person metadata
    person = db_metadata["Person"]
    assert person.exist
    assert len(person) == 2
    assert "name" in person
    assert person.cls is Person

    # check attr name metadata
    name_attr = person["name"]
    assert name_attr.name == "name"
    assert name_attr.type == str
    assert name_attr.atomic_type == str
    assert name_attr.atomic_type_name == "str"
    assert not name_attr.unique
    assert not name_attr.many
    assert not name_attr.ref
    assert not name_attr.referenced_by
    assert name_attr.exist

    # check attr animal metadata
    animal_attr = person["animal"]
    assert animal_attr.name == "animal"
    assert animal_attr.type == "Animal"
    assert animal_attr.atomic_type == "Animal"
    assert animal_attr.atomic_type_name == "Animal"
    assert not animal_attr.unique
    assert not animal_attr.many
    assert animal_attr.ref == "owner"
    assert not animal_attr.referenced_by
    assert animal_attr.exist

    # check cls Animal metadata (at this stage we don't have information about the cls)
    animal = db_metadata["Animal"]
    assert len(animal) == 1
    assert not animal.exist

    # Check attribute owner
    owner_attribute = animal["owner"]
    assert not owner_attribute.exist
    assert owner_attribute.name == "owner"
    # assert owner_attribute.type is None  # we can't now if it's a List or not
    assert owner_attribute.atomic_type == Person
    assert owner_attribute.atomic_type_name == "Person"
    assert not owner_attribute.unique
    assert owner_attribute.many is None
    assert owner_attribute.ref is None
    assert owner_attribute.referenced_by is animal_attr
    assert not owner_attribute.exist


# TODO: test two class
# TODO: test two classes with reference

# TODO: test if builtin type
@pytest.mark.skip
def test_relationaldbmetadata_one_cls_relationaldb_metadata():
    """Test the metadata of one simple class"""
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute(unique=True)
        animal: "Animal" = db.attribute(ref="owner")

    # Check class metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 2
    assert "Person" in db_metadata
    assert "Animal" in db_metadata

    # check cls metadata
    person = db_metadata["Person"]
    assert len(person) == 2
    assert person.cls is Person

    # check name metadata
    # check attr metadata
    assert "name" in person
    name_attr = person["name"]
    assert name_attr.name == "name"
    assert name_attr.type == str
    assert name_attr.atomic_type_name == "str"
    assert not name_attr.unique
    assert not name_attr.many
    assert name_attr.ref == "owner"
    assert not name_attr.referenced_by


def test_error_ref_builtin_attribute():
    for type in [str, int, float, bool]:
        db = relationaldb()

        with pytest.raises(ValueError):
            # We cannot reference built-in attribute
            @db.register
            class Person:
                attribute: type = db.attribute(ref="attr")


def test_error_ref_no_existing_attribute():
    db = relationaldb()

    @db.register
    class Person:
        name: db.attribute()

    with pytest.raises(ValueError):

        @db.register
        class Animal:
            name: db.attribute()
            owner: Person = db.attribute(ref="animal")


def test_relationaldb_metadata_one_cls_with_list():
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute()
        animals: List["Animal"] = db.attribute()

    # Check class metadata
    db_metadata = db.db_metadata
    assert len(db_metadata) == 1
    person = db_metadata["Person"]

    assert len(person) == 2
    assert "animals" in person

    # check animals metadata
    animals_attribute = person["animals"]
    assert animals_attribute.name == "animals"
    assert animals_attribute.type == List["Animal"]
    assert animals_attribute.atomic_type_name == "Animal"
    assert not animals_attribute.unique
    assert animals_attribute.many
    assert not animals_attribute.ref
    assert not animals_attribute.referenced_by


@pytest.mark.skip(reason="Not implemented yet")
def test_many_many():
    db = relationaldb()

    @db.register
    class Person:
        name: str = db.attribute(unique=True)
        animals: List["Animal"]

    @db.register
    class Animal:
        name: str
        owners: List[Person] = db.attribute(ref="animals")

    foo = Person("foo")
    bar = Person("bar")
    ploofy = Animal("ploofy")
    rex = Animal("rex")

    foo.animals.append(ploofy)
    assert ploofy in foo.animals
    assert foo in ploofy.owners

    db.first("Animal", name="foo")
