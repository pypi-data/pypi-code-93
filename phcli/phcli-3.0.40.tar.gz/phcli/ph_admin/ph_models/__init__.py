import uuid
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Partner(Base):
    __tablename__ = 'partner'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    address = Column(String)
    phoneNumber = Column(String)
    web = Column(String)
    employee = Column(String, default='{}')
    accounts = relationship('Account', back_populates="partner")
    created = Column(String, default=datetime.now())
    modified = Column(String, default=datetime.now())

    def __repr__(self):
        return str(self.__dict__)


class Account(Base):
    __tablename__ = 'account'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    wechatOpenId = Column(String)
    password = Column(String)
    phoneNumber = Column(String)
    defaultRole = Column(String, ForeignKey('role.id'))
    role = relationship('Role', back_populates='accounts')
    email = Column(String)
    employer = Column(String, ForeignKey('partner.id'))
    partner = relationship('Partner', back_populates='accounts')
    created = Column(String, default=datetime.now())
    modified = Column(String, default=datetime.now())
    firstName = Column(String)
    lastName = Column(String)

    def __repr__(self):
        return str(self.__dict__)


class Role(Base):
    __tablename__ = 'role'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    accountRole = Column(String, default='{}')
    accounts = relationship('Account', back_populates="role")
    description = Column(String)
    scope = Column(String, default='{}')
    created = Column(String, default=datetime.now())
    modified = Column(String, default=datetime.now())

    def __repr__(self):
        return str(self.__dict__)


class Scope(Base):
    __tablename__ = 'scope'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    description = Column(String)
    scopePolicy = Column(String)
    owner = Column(String, default='{}')
    created = Column(String, default=datetime.now())
    modified = Column(String, default=datetime.now())

    def __repr__(self):
        return str(self.__dict__)


if __name__ == '__main__':
    import base64
    from phcli.ph_db.ph_pg import PhPg

    pg = PhPg(
        base64.b64decode('cGgtZGItbGFtYmRhLmNuZ2sxamV1cm1udi5yZHMuY24tbm9ydGh3ZXN0LTEuYW1hem9uYXdzLmNvbS5jbgo=').decode('utf8')[:-1],
        base64.b64decode('NTQzMgo=').decode('utf8')[:-1],
        base64.b64decode('cGhhcmJlcnMK').decode('utf8')[:-1],
        base64.b64decode('QWJjZGUxOTYxMjUK').decode('utf8')[:-1],
        db=base64.b64decode('cGhjb21tb24K').decode('utf8')[:-1],
    )

    pn = Partner(name="test", address="test", phoneNumber="test", web="test")
    pn = pg.insert(pn)
    pn = pg.query(pn)
    pn = pn[0] if pn else None

    ac = Account(name="test", wechatOpenId="test", password="test", phoneNumber="test",
                 email='test', firstName='test', lastName='test')
    ac.partner = pn
    ac = pg.insert(ac)
    pg.update(Partner(id=pn.id, employee=pn.employee+[ac.id]))

    ac2 = Account(name="test2", wechatOpenId="test2", password="test2", phoneNumber="test2",
                  email='test2', firstName='test2', lastName='test2')
    ac2.partner = pn
    ac2 = pg.insert(ac2)
    pg.update(Partner(id=pn.id, employee=pn.employee+[ac2.id]))

    pg.commit()



