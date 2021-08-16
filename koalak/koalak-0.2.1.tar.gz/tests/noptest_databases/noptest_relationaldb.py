import tempfile
from typing import Dict, List

import koala
import pytest
from koala import RelationalDB, relationaldb


def test_relationaldb_simple():
    def db_factory(name):
        db = relationaldb(name)

        @db.table("persons")
        class Person:
            name: str = db.attribute()
            age: int = db.attribute()

        db.init()
        return db, Person

    with tempfile.NamedTemporaryFile() as f:
        db, Person = db_factory(f.name)
        # Add 3 persons to the db
        Person("Foo", 25)
        Person("Bar", 28)
        baz = Person("Baz", 20)
        baz.age = 22
        # FIXME: db.close()?
        db.close()
        # recreate the db to check persistance
        db, Person = db_factory(f.name)
        foo = db.query(Person).filter_by(name="Foo").first()
        assert foo.name == "Foo"
        assert foo.age == 25

        baz = db.query(Person).filter_by(name="Baz").first()
        assert baz.name == "Baz"
        assert baz.age == 22


def test_relationaldb_query():
    def db_factory(name):
        db = relationaldb(name)

        @db.table("Person")
        class Person:
            name: str = db.attribute()
            age: int = db.attribute()

        db.init()

        return db, Person

    with tempfile.NamedTemporaryFile() as f:
        db, Person = db_factory(f.name)

        foo = Person("foo", 20)
        assert foo.name == "foo"
        assert foo.age == 20
        bar = Person("bar", 21)
        baz = Person("baz", 22)

        assert len(list(db.query(Person))) == 3
        assert db.query(Person).filter_by(name="foo").first() is foo
        assert db.query(Person).filter_by(age=21).first() is bar

        assert len(list(db.query(Person).filter(Person.age >= 21))) == 2
        db.close()
        # REBUILD THE DB TO CHECK PERSISTENCE
        db, Person = db_factory(f.name)
        foo = db.first(Person, name="foo")
        bar = db.first(Person, name="bar")
        baz = db.first(Person, name="baz")

        assert foo.name == "foo"
        assert foo.age == 20
        assert bar.name == "bar"
        assert bar.age == 21
        assert baz.name == "baz"
        assert baz.age == 22


def test_relationaldb_first():
    # use sqlalchemy
    db = relationaldb()

    @db.table("persons")
    class Person:
        name: str = db.attribute()
        age: int = db.attribute()

    db.init()

    foo = Person("foo", 20)
    bar = Person("bar", 21)
    baz = Person("baz", 22)
    assert db.first(Person, name="foo") is foo
    assert db.first("persons", name="bar") is bar
    assert db.first("persons", name="baz") is baz


def test_one_to_many_relation_not_null_no_backref_with_ref_as_cls():
    def db_factory(name):
        db = relationaldb(name)

        @db.table("persons")
        class Person:
            name: str = db.attribute()
            age: int = db.attribute()
            # animals = db.attribute(type=db.List["Animal"], backref=True)

        @db.table("animals")
        class Animal:
            owner: Person = db.attribute()
            name: str = db.attribute()

        db.init()

        return db, Person, Animal

    with tempfile.NamedTemporaryFile() as f:
        db, Person, Animal = db_factory(f.name)
        with db:
            foo = Person("foo", 20)
            bar = Person("bar", 21)
            baz = Person("baz", 22)
            assert db.first(Person, name="foo") is foo
            assert db.first("persons", name="bar") is bar
            assert db.first("persons", name="baz") is baz

            afoo = Animal(foo, "afoo")
            assert afoo.owner is foo
            assert afoo.name == "afoo"

            afoo.owner = bar
            assert afoo.owner is bar
            assert afoo.name == "afoo"
            # import ipdb; ipdb.set_trace()
        # Rebuild to test persistence
        db, Person, Animal = db_factory(f.name)
        with db:
            afoo = db.first(Animal, name="afoo")
            bar = db.first(Person, name="bar")
            assert afoo.owner is bar

    # TODO fix all tests with factory


def test_one_to_many_relation_not_null_no_backref_with_ref_as_cls_inverse_order():
    def db_factory(name):
        db = relationaldb(name)

        @db.table("animals")
        class Animal:
            owner: "Person" = db.attribute()
            name: str = db.attribute()

        @db.table("persons")
        class Person:
            name: str = db.attribute()
            age: int = db.attribute()
            # animals = db.attribute(type=db.List["Animal"], backref=True)

        db.init()

        return db, Person, Animal

    with tempfile.NamedTemporaryFile() as f:
        db, Person, Animal = db_factory(f.name)
        with db:
            foo = Person("foo", 20)
            bar = Person("bar", 21)
            baz = Person("baz", 22)
            assert db.first(Person, name="foo") is foo
            assert db.first("persons", name="bar") is bar
            assert db.first("persons", name="baz") is baz

            afoo = Animal(foo, "afoo")
            assert afoo.owner is foo
            assert afoo.name == "afoo"

            afoo.owner = bar
            assert afoo.owner is bar
            assert afoo.name == "afoo"
            # import ipdb; ipdb.set_trace()
        # Rebuild to test persistence
        db, Person, Animal = db_factory(f.name)
        with db:
            afoo = db.first(Animal, name="afoo")
            bar = db.first(Person, name="bar")
            assert afoo.owner is bar


def test_one_to_many_relation_not_null_no_backref_with_ref_as_str():
    def db_factory(name):
        db = relationaldb(name)

        @db.table("persons")
        class Person:
            name: str = db.attribute()
            age: int = db.attribute()

        @db.table("animals")
        class Animal:
            owner = db.attribute(type="Person")
            name: str = db.attribute()

        db.init()
        return db, Person, Animal

    with tempfile.NamedTemporaryFile() as f:
        db, Person, Animal = db_factory(f.name)
        with db:
            foo = Person("foo", 20)
            bar = Person("bar", 21)
            baz = Person("baz", 22)
            assert db.first(Person, name="foo") is foo
            assert db.first("persons", name="bar") is bar
            assert db.first("persons", name="baz") is baz

            afoo = Animal(foo, "afoo")
            assert afoo.owner is foo
            assert afoo.name == "afoo"

            afoo.owner = bar
            assert afoo.owner is bar
            assert afoo.name == "afoo"
            # TODO: test that it's not nullable!

        db, Person, Animal = db_factory(f.name)
        with db:
            afoo = db.first(Animal, name="afoo")
            bar = db.first(Person, name="bar")
            assert afoo.owner is bar
            assert afoo.name == "afoo"


def test_one_to_many_relation_null_no_backref_with_ref_as_cls():
    def db_factory(name):
        db = relationaldb(name)

        @db.table("persons")
        class Person:
            name: str = db.attribute()
            age: int = db.attribute()

        @db.table("animals")
        class Animal:
            name: str = db.attribute()
            owner: Person = db.attribute(default=None)

        db.init()
        return db, Person, Animal

    with tempfile.NamedTemporaryFile() as f:
        db, Person, Animal = db_factory(f.name)
        with db:
            foo = Person("foo", 20)
            bar = Person("bar", 21)
            baz = Person("baz", 22)
            assert db.first(Person, name="foo") is foo
            assert db.first("persons", name="bar") is bar
            assert db.first("persons", name="baz") is baz

            afoo = Animal("afoo", foo)
            assert afoo.owner is foo
            assert afoo.name == "afoo"

            afoo.owner = bar
            assert afoo.owner is bar
            assert afoo.name == "afoo"

            abar = Animal("abar")
            assert abar.owner is None
            assert abar.name == "abar"

        db, Person, Animal = db_factory(f.name)
        with db:
            foo = db.first(Person, name="foo")
            bar = db.first(Person, name="bar")
            baz = db.first(Person, name="baz")
            afoo = db.first(Animal, name="afoo")
            abar = db.first(Animal, name="abar")

            assert afoo.owner is bar
            assert afoo.name == "afoo"

            assert abar.owner is None
            assert abar.name == "abar"


def test_error_referencing_non_existing_attribute_before_init():
    db = relationaldb()

    @db.table("persons")
    class Person:
        name: str = db.attribute()

    with pytest.raises(ValueError):

        @db.table("animals")
        class Animal:
            name: str = db.attribute()
            owner: Person = db.attribute(default=None, ref="age")


@pytest.mark.skip
def test_one_to_many_relation_null_backref_with_ref_as_cls():
    # TODO: implement, one to many, and many to one with different relations side
    def db_factory(name):
        db = relationaldb(name)

        @db.table("persons")
        class Person:
            name: str = db.attribute()
            age: int = db.attribute()
            animals: db.List["Animal"] = db.attribute(ref="owner", factory=list)

        @db.table("animals")
        class Animal:
            name: str = db.attribute()
            owner: Person = db.attribute(default=None)

        db.init()
        return db, Person, Animal

    with tempfile.NamedTemporaryFile() as f:
        db, Person, Animal = db_factory(f.name)

        foo = Person("foo", 20)
        bar = Person("bar", 21)
        baz = Person("baz", 22)

        assert not foo.animals
        assert db.first(Person, name="foo") is foo
        assert db.first("persons", name="bar") is bar
        assert db.first("persons", name="baz") is baz

        afoo = Animal("afoo", foo)
        db.commit()
        assert afoo.owner is foo
        assert afoo.name == "afoo"
        assert afoo in foo.animals

        afoo.owner = bar
        assert afoo.owner is bar
        assert afoo.name == "afoo"

        abar = Animal("abar")
        assert abar.owner is None
        assert abar.name == "abar"


def test_self_referencing_one_to_many_no_backref():
    db = relationaldb()

    @db.table("persons")
    class Person:
        name: str = db.attribute()
        age: int = db.attribute()
        best_friend = db.attribute(type="Person", default=None)

    db.init()

    # TODO: add same test with ref
    # TODO: add this test with many to many
    # TODO: add test that rise error if nullable is true when impossible, like in self referencing, nullable must be True (or set it to False automatticaly)
    foo = Person("foo", 21)
    assert foo.name == "foo"
    assert foo.age == 21
    assert foo.best_friend is None

    bar = Person("bar", 22)
    assert bar.name == "bar"
    assert bar.age == 22
    assert bar.best_friend is None

    foo.best_friend = bar
    assert foo.best_friend is bar
    assert bar.best_friend is None


def notest_complecated_relations():
    # FINAL TEST TO PASS?
    # TODO: activate me (rename notest to test)
    db = relationaldb()

    @db.table("persons")
    class Person:
        name: str = db.attribute()
        # persons (recursive)
        # a person to love

        # crush (one-to-many)
        crush = db.attribute(type="Person")
        my_lovers = db.attribute(type=db.List["Person"], relation=crush)

        # best friend (one-to-many)
        best_friend = db.attribute(type="Person")
        best_friend_of = db.attribute(type=db.List["Person"], relation=best_friend)

        # best animal (one-to-many)
        best_animal = db.attribute(type="Animal")

        # worst animal (one-to-many)
        worst_animal = db.attribute(type="Animal")

        # friends (many-to-many) (A can be a friend of B and B is not a friend of A, not transitive)
        friends = db.attribute(type=db.List["Person"])
        friends_of = ...
        exes = db.attribute(type=db.List["Person"])
        # animals
        prefered_animals = db.attribute(type=db.List["Animal"])
        owned_animals = db.attribute(type=db.List["Animal"])

        # test with hate and haters both ways
        hate = db.attribute(type="Person")
        haters = db.attribute(type=db.List["Person"], relation=hate)

        # or
        haters = db.attribute(type=db.List["Person"], many=False)
        hate = db.attribute(type="Person", relation=haters)
        # TODO: write example in koala/examples/relationaldb.py convert doc sqlalchemy to my syntax

    @db.table("animals")
    class Animal:
        name: str = db.attribute()
        crush: str = db.attribute(type="Animal")
        friends: str = db.attribute(type=db.List["Animal"])
        # persons
        prefered_persons: db.List[Person] = db.attribute()
        owners: db.List[Person] = db.attribute()
        best_owner: Person = db.attribute()
        worst_owner: Person = db.attribute()

        # backref
        persons_that_prefer_me: db.List[Person] = db.attribute(
            backref="prefered_animals"
        )


def notest_budget_example_app():
    db = relationaldb()

    @db.table("budgets")
    class Budget:
        name: str = db.attribute()
        initial_balance: int = db.attribute(default=0)
        description: str = db.attribute(default="")

        balance: int = db.attribute(init=False)

        transactions = db.attribute(type=db.List["Transaction"], relation="budget")

    @db.table("transactions")
    class Transaction:
        budget: Budget = db.attribute()
        value: int = db.attribute()
        description: str = db.attribute()

    @db.table("categories")
    class Categorie:
        name: str = db.attribute()
        description: str = db.attribute(default="")

    @db.table("tags")
    class Tag:
        name: str = db.attribute()
        description: str = db.attribute(default="")

    @db.table("animal")
    class Animal:
        name: str
        age: int


# TEST INTERNALS STATE


def test_building_attributes_one_simple_table():
    db = relationaldb()
    building_class = db._building_class

    @db.table("persons")
    class Person:
        name: str = db.attribute()
        age: int = db.attribute()

    assert len(building_class) == 1
    assert "Person" in building_class
    building_cls_person = building_class["Person"]
    assert building_cls_person.name == "Person"
    assert building_cls_person.table_name == "persons"
    assert building_cls_person.orm_cls is Person
    assert building_cls_person.exist
    assert len(building_cls_person.attributes) == 0


def test_building_attributes_one_two_table():
    db = relationaldb()
    building_class = db._building_class

    @db.table("persons")
    class Person:
        name: str = db.attribute()
        age: int = db.attribute()

    assert len(building_class) == 1
    assert "Person" in building_class
    building_cls_person = building_class["Person"]
    assert building_cls_person.name == "Person"
    assert building_cls_person.table_name == "persons"
    assert building_cls_person.orm_cls is Person
    assert building_cls_person.exist
    assert len(building_cls_person.attributes) == 0

    @db.table("animals")
    class Animal:
        name: str = db.attribute()

    assert len(building_class) == 2
    assert "Person" in building_class
    assert "Animal" in building_class

    building_cls_person = building_class["Person"]
    assert building_cls_person.name == "Person"
    assert building_cls_person.table_name == "persons"
    assert building_cls_person.orm_cls is Person
    assert building_cls_person.exist
    assert len(building_cls_person.attributes) == 0

    building_cls_animal = building_class["Animal"]
    assert building_cls_animal.name == "Animal"
    assert building_cls_animal.table_name == "animals"
    assert building_cls_animal.orm_cls is Animal
    assert building_cls_animal.exist
    assert len(building_cls_animal.attributes) == 0


def test_building_attributes_two_table_with_relation():
    db = relationaldb()
    building_class = db._building_class

    @db.table("persons")
    class Person:
        name: str = db.attribute()
        age: int = db.attribute()

    assert len(building_class) == 1
    assert "Person" in building_class
    building_cls_person = building_class["Person"]
    assert building_cls_person.name == "Person"
    assert building_cls_person.table_name == "persons"
    assert building_cls_person.orm_cls is Person
    assert building_cls_person.exist
    assert len(building_cls_person.attributes) == 0

    @db.table("animals")
    class Animal:
        name: str = db.attribute()
        owner: Person = db.attribute()

    assert len(building_class) == 2
    assert "Person" in building_class
    assert "Animal" in building_class

    building_cls_person = building_class["Person"]
    assert building_cls_person.name == "Person"
    assert building_cls_person.table_name == "persons"
    assert building_cls_person.orm_cls is Person
    assert building_cls_person.exist
    assert len(building_cls_person.attributes) == 0

    building_cls_animal = building_class["Animal"]
    assert building_cls_animal.name == "Animal"
    assert building_cls_animal.table_name == "animals"
    assert building_cls_animal.orm_cls is Animal
    assert building_cls_animal.exist
    assert len(building_cls_animal.attributes) == 1

    owner_attribute = building_cls_animal.attributes["owner"]
    assert owner_attribute.name == "owner"
    assert not owner_attribute.many
    assert owner_attribute.atomic_type_name == "Person"
    assert owner_attribute.referenced_by is None
    assert owner_attribute.exist is True


def test_building_attributes_one_table_with_relation():
    db = relationaldb()

    building_class = db._building_class

    @db.table("persons")
    class Person:
        name: str = db.attribute()
        age: int = db.attribute()
        animal: "Animal" = db.attribute()

    print("building_class", building_class)
    assert len(building_class) == 2
    assert "Person" in building_class
    building_cls_person = building_class["Person"]
    assert building_cls_person.name == "Person"
    assert building_cls_person.table_name == "persons"
    assert building_cls_person.orm_cls is Person
    assert building_cls_person.exist

    assert len(building_cls_person.attributes) == 1

    animal_attribute = building_cls_person.attributes["animal"]
    assert animal_attribute.name == "animal"
    assert animal_attribute.exist
    assert not animal_attribute.many
    assert animal_attribute.atomic_type_name == "Animal"
    assert animal_attribute.referenced_by is None

    building_cls_animal = building_class["Animal"]
    assert not building_cls_animal.exist


def notest_relationaldb_dict():
    db = relationaldb()

    @db.register
    class Person:
        name: str
        animal: "Animal" = db.attribute(ref="owner")

    @db.register
    class Animal:
        name: str
        owner: Person

    foo = Person("foo")
    bar = Person("bar")
    ploofy = Animal("ploofy")

    foo.animal = ploofy
    assert ploofy.owner is foo


class Person:
    def __init__(self, name: str, animal=None):
        self._animal = None

        self.name = name
        self.animal = animal

    @property
    def animal(self):
        return self._animal

    @animal.setter
    def animal(self, animal):
        if animal is None:
            if self._animal:
                self._animal._owner = None
            self._animal = animal

        if getattr(self, "_animal", False):
            self._animal._owner = None
        self._animal = animal
        animal._owner = self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


class Animal:
    def __init__(self, name, owner=None):
        self.name = name
        self.owner = owner

    @property
    def owner(self):
        return self._animal

    @owner.setter
    def owner(self, owner):
        if getattr(self, "_owner", False):
            self._owner._animal = None
        self._owner = owner
        owner._animal = self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"
