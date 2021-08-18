import datetime
import random

# ==================== TEST BUDGET ============
import sys
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

echo = len(sys.argv) > 1
# print("echo", echo)
engine = create_engine("sqlite:///:memory:", echo=echo)
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
        print("AAAAAAAAAAAAAAAa")
        self.balance = self.initial_balance
        self.refunded_balance = self.initial_balance


old_init = BudgetBase.__attrs_post_init__


def new_init(self):
    print("BBBBBBBBBBBBBBBBB")
    old_init(self)
    print(self)
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


def new_init2(self):
    old_init2(self)
    session.add(self)
    session.commit()


TransactionBase.__attrs_post_init__ = new_init2


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


Base.metadata.create_all(engine)
session = Session()

bnp = Budget("bnp")
print(bnp)

t1 = Transaction(bnp, 100, "phone")
print(t1)

# =================== END TEST ================
