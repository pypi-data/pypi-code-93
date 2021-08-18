# ================
import datetime
import random
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
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine("sqlite:///:memory:", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

"""
for a simple one-to-many there are 2 differents interpratation for relationship
Ex: class Person:  best_friend_id  ...
- the object pointing to (the best_friend)
- all object pointing to me (i am the bestfriend of...) (BY DEFAULT)
# by default p


Ex2:   class Animal: owner_id
- Animal: owner
- Person: animals
"""


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name: str = Column(String)
    age: int = Column(Integer)
    best_friend_id = Column(Integer, ForeignKey("persons.id"))
    ref = relationship("Person")
    # best_friend = relationship("Person", foreign_keys=best_friend_id, uselist=False)
    # best_friend_of = relationship("Person", remote_side=id)
    # best_friend = relationship("Person")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


Base.metadata.create_all(engine)
session = Session()


foo = Person(name="foo", age=20)
bar = Person(name="bar", age=21)
print(foo.red)


engine = create_engine("sqlite:///:memory:", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    billing_address_id = Column(Integer, ForeignKey("address.id"))
    shipping_address_id = Column(Integer, ForeignKey("address.id"))
    customer_id = Column(Integer, ForeignKey("customer.id"))

    billing_address = relationship("Address", foreign_keys=billing_address_id)
    customer = relationship("Customer", foreign_keys=customer_id)
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.city})"


Base.metadata.create_all(engine)
session = Session()

a1 = Address(street="12", city="city", state="state", zip="zip")
a2 = Address(street="13", city="2", state="2", zip="2")

session.add(a1)
session.add(a2)
session.commit()
foo = Customer(name="foo")
bar = Customer(name="bar")
print(foo.customer)


# ==================
engine = create_engine("sqlite:///:memory:", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name: str = Column(String)
    age: int = Column(Integer)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


class Animal(Base):
    __tablename__ = "animals"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("persons.id"))
    name: str = Column(String)
    owner = relationship("Person", foreign_keys="Animal.owner_id")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


Base.metadata.create_all(engine)
session = Session()

foo = Person(name="foo", age=20)
bar = Person(name="bar", age=21)

session.add(foo)
session.add(bar)
session.commit()


afoo = Animal(name="afoo", owner=foo)
session.add(afoo)
session.commit()

# STRATEGY: apply attr => inherit from attr

# ==================== TEST BUDGET ============
engine = create_engine("sqlite:///:memory:", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


@attr.s
class BudgetBase:
    name: str = attr.ib()
    initial_balance: int = attr.ib(default=0)
    description: str = attr.ib(default=True, kw_only=True)
    creation_date = attr.ib(factory=datetime.datetime.utcnow)
    loan: bool = attr.ib(default=True, kw_only=True)
    frm = attr.ib(default=None, kw_only=True)
    balance = attr.ib(init=False)
    refunded_balance = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.balance = self.initial_balance
        self.refunded_balance = self.initial_balance


old_init = BudgetBase.__attrs_post_init__


def new_init(self):
    old_init(self)
    session.add(self)
    session.commit()


BudgetBase.__attrs_post_init__ = new_init


class Budget(BudgetBase, Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    loan = Column(Boolean, default=True, nullable=False)
    id_from = Column(Integer, ForeignKey("budgets.id"), nullable=True)

    # balance
    initial_balance = Column(Integer, nullable=False)
    balance = Column(Integer, nullable=False)
    refunded_balance = Column(Integer, nullable=False)

    @property
    def transactions(self):
        return session.query(Transaction).filter_by(id_budget=self.id)


@attr.s
class TransactionBase:
    budget: Budget = attr.ib()
    value: int = attr.ib()
    description: str = attr.ib(default="")
    affected: Budget = attr.ib(default=None)
    loan: bool = attr.ib(default=False)

    def __attrs_post_init__(self):
        pass


old_init2 = TransactionBase.__attrs_post_init__


def new_init(self):
    old_init2(self)
    session.add(self)
    session.commit()


BudgetBase.__attrs_post_init__ = new_init


class Transaction(TransactionBase, Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    id_budget = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    id_affected_budget = Column(Integer, ForeignKey("budgets.id"), nullable=True)
    time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    value = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    loan = Column(Boolean, default=True, nullable=False)

    # transactions
    @property
    def budget(self):
        return session.query(Budget).filter_by(id=self.id_budget).first()

    @budget.setter
    def budget(self, value):
        self.id_budget = value.id


bnp = Budget("bnp")
print(bnp)

t1 = Transaction(bnp, 100, "phone")
print(t1)

# =================== END TEST ================
attributes = {
    "id": Column(Integer, primary_key=True),
    "name": Column(String),
    "age": Column(Integer),
}
x = Person.__attrs_attrs__


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    creation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    loan = Column(Boolean, default=True, nullable=False)
    id_from = Column(Integer, ForeignKey("budgets.id"), nullable=True)

    # balance
    initial_balance = Column(Integer, nullable=False)
    balance = Column(Integer, nullable=False)
    refunded_balance = Column(Integer, nullable=False)

    def __init__(
        self,
        name,
        initial_balance,
        description="",
        creation_date=None,
        loan=False,
        frm=None,
    ):
        self.name = name
        self.initial_balance = initial_balance
        self.description = description
        if creation_date is None:
            self.creation_date = datetime.datetime.utcnow()
        self.loan = loan
        self.frm = frm
        self.balance = initial_balance
        self.refunded_balance = initial_balance
        session.add(self)
        session.commit()

    def __repr__(self):
        return f"Budget({self.name})"

    @property
    def transactions(self):
        return session.query(Transaction).filter_by(id_budget=self.id)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    id_budget = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    id_affected_budget = Column(Integer, ForeignKey("budgets.id"), nullable=True)
    time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    value = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    loan = Column(Boolean, default=True, nullable=False)

    def __init__(self, budget, value, description="", affected=None, loan=False):
        self.budget = budget
        self.value = value
        self.description = description
        self.affected = affected
        self.loan = loan
        session.add(self)
        session.commit()

    def __repr__(self):
        return f"Transaction({self.description}, {self.value})"

    # transactions
    @property
    def budget(self):
        return session.query(Budget).filter_by(id=self.id_budget).first()

    @budget.setter
    def budget(self, value):
        self.id_budget = value.id


Base.metadata.create_all(engine)
session = Session()


bnp = Budget("bnp", 1000)
mama = Budget("mama", 2000)
print(bnp)
print(mama)

t1 = Transaction(bnp, 100, "bazef")
t2 = Transaction(bnp, 50, "test")
for i in range(20):
    print(i)
    budget = random.choice([bnp, mama])
    value = random.randint(-100, 100)
    des = random.choice(["phone", "test", "some", "thing", "well"])
    print(budget, value, des)
    Transaction(budget, value, des)


print(t1)
print(t2)

print(bnp.transactions)
for t in bnp.transactions:
    print(t)
