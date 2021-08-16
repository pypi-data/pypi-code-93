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


@attr.s
class Budget:
    name = attr.ib()
    initial_balance = attr.ib(default=0)
    transactions = attr.ib(factory=list)
    frm = attr.ib(default=None)
    loan = attr.ib(default=False)
    balance = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.balance = self.initial_balance


@attr.s
class Transaction:
    # budget = attr.ib(repr=False)
    value = attr.ib()
    description = attr.ib()
    # If the transaction affect an other budget
    affect = attr.ib(default=None)
    loan = attr.ib(default=False)


engine = create_engine("sqlite:///:memory:", echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()


attributes = {
    "__tablename__": "budgets",
    "id": Column(Integer, primary_key=True),
    "name": Column(String),
    "loan": Column(Boolean, default=True, nullable=False),
    "frm": Column(Integer, ForeignKey("budgets.id"), nullable=True),
    "initial_balance": Column(Integer, default=0, nullable=False),
    "balance": Column(Integer, nullable=False),
    # "transactions": property()
    "__init__": Budget.__init__,
    "__attrs_post_init__": Budget.__attrs_post_init__,
    "__repr__": Budget.__repr__,
}
BudgetORM = type("BudgetORM", (Base,), attributes)

# transactions
@property
def budget(self):
    session.query(BudgetORM).filter_by(id=self.id_budget).first()


@budget.setter
def budget(self, value):
    self.id_budget = value.id


attributes = {
    "__tablename__": "transactions",
    "id": Column(Integer, primary_key=True),
    "id_budget": Column(Integer, ForeignKey("budgets.id"), nullable=False),
    "id_affected_budget": Column(Integer, ForeignKey("budgets.id"), nullable=True),
    "value": Column(Integer, default=0, nullable=False),
    "description": Column(Integer, nullable=False),
    "loan": Column(Boolean, default=True, nullable=False),
    # "transactions": property()
    "__init__": Transaction.__init__,
    "__repr__": Transaction.__repr__,
    "budget": budget,
}

TransactionORM = type("TransactionORM", (Base,), attributes)

Base.metadata.create_all(engine)
session = Session()

bnp = BudgetORM("bnp", 1000)
print(bnp)
session.add(bnp)
session.commit()

t = TransactionORM(bnp, 100, "bazef")
print(t)
