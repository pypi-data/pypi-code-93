import datetime
import tempfile

import attr
import pytest
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# ===== #
# TESTS #
# ===== #
def tes_relational_one_to_n():
    class Person:
        def __init__(self, name):
            self.name = name
            self.animals = []

    class Animal:
        def __init__(self, owner, name):
            self.owner = owner
            self.name = name

    person = Person("person")
    animal = Animal(person, "animal")


def t2():
    @attr.s
    class Person:
        name = attr.ib()
        # 0:n
        animals = relation("0:n")

    @attr.s
    class Animal:
        owner = relation("0:1", Person.animals)
        name = attr.ib()

    person = Person("person")
    animal = Animal(person, "animal")
    assert animal in person.animals

    animal2 = Animal("woofy")
    person2 = Person("person2")
    person2.animals.append(animal2)
    assert animal2.owner is person2


def t_db_0_n_to_0_n():
    class Person:
        name = attribute()
        animals = attribute("n")

    class Animal:
        name = attribute()
        owners = attribute("n", Person.animals)

    p1 = Person("p1")
    a1 = Animal("a1")
    p1.animals.append(a1)
    assert p1 in a1.owners


def t_db_one_to_many():
    db = Relational("budgetm")

    @db.table("transactions")
    @attr.s
    class Transaction:
        value = attr.ib()

    @db.table("budgets")
    @attr.s
    class Budget:
        name = attr.ib()
        transactions = attr.ib(factory=list)

    bnp = Budget("bnp")
    bnp.transactions.append(Transaction(30))
    bnp.transactions.append(Transaction(-20))
    print(bnp)


def t272414():
    db = Relational()

    @db.table("budgets")  # primary key is id
    class Budget:
        name = db.Collumn(db.String)
        transactions = db.relational(table="transactions", target="budget")
        frm_budget = db.Collumn("budgets", nullable=True)

    @db.table("transactions")
    class Transaction:
        value = db.Collumn(db.Integer)
        budget = ...


def tes_rNelationaldb_simple():
    @attr.s
    class Animal:
        name: str = attr.ib()
        age: int = attr.ib()

    with tempfile.NamedTemporaryFile() as f:
        db = Relational(f.name, echo=True)
        db.table("animals")(Animal)
        db.init()

        animal = Animal("woofy", 25)
        print(animal)
        db = Relational(f.name, echo=True)
        db.table("animals")(Animal)
        db.init()

        assert db.query(Animal).first(name="woofy").age == 25


def test_rNelationaldb_relation():
    db = Relational(echo=True)

    @db.table("budgets")
    class Budget:
        name: str = db.attribute(unique=True)
        initial_balance: int = db.attribute()
        # from now only accept key words only
        # kw_only = db.kw_only()# TODO: later
        description: str = db.attribute(default="", kw_only=True)
        frm = db.attribute(type="budgets", default=None, kw_only=True)
        creation_date: DateTime = db.attribute(factory=db.datetime_now, kw_only=True)
        loan: bool = db.attribute(default=False, kw_only=True)

        # balance
        balance: int = db.attribute(init=False)
        refunded_balance: int = db.attribute(init=False)

        def __attrs_post_init__(self):
            self.balance = self.initial_balance
            self.refunded_balance = self.initial_balance

    @db.table("transactions")
    class Transaction:
        budget: Budget = db.attribute(target="transactions")
        value: int = db.attribute()
        description: str = db.attribute()
        # _kw_only = db.kw_only()
        affected_budget = db.attribute(type="budgets", default=None, kw_only=True)
        time: DateTime = db.attribute(factory=db.datetime_now, kw_only=True)
        loan: bool = db.attribute(default=False, kw_only=True)

    db.init()

    bnp = Budget("bnp", 1000)
    bnp_fromdb = db.query(Budget).filter_by(name="bnp").first()
    assert bnp is bnp_fromdb

    t1 = Transaction(bnp, 300, "printer")
    assert t1 in bnp.transactions
    assert list(bnp.transactions) == [t1]

    assert t1.budget is bnp

    # get bnp budget


@attr.s
class Point:
    x: int = attr.ib()
    y: int = attr.ib(default=0, repr=False)
