import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Float


Base = declarative_base()


class Asset(Base):
    __tablename__ = 'asset'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    owner = Column(String)
    extension = Column(String, default='parquet')
    block = Column(String, default='{}')
    size = Column(Float, default=-1)
    providers = Column(String, default='{}')
    markets = Column(String, default='{}')
    molecules = Column(String, default='{}')
    dateCover = Column(String, default='{}')
    geoCover = Column(String, default='{}')
    labels = Column(String, default='{}')
    created = Column(DateTime, default=datetime.now())
    modified = Column(DateTime, default=datetime.now())
    description = Column(String)
    type = Column(String, default='file')
    source = Column(String)
    version = Column(String, default='0.0.1')
    isNewVersion = Column(String, default='t')
    accessibility = Column(String, default='w')
    shared = Column(String)
    partners = Column(String)

    def __repr__(self):
        return str(self.__dict__)


if __name__ == '__main__':
    asset = Asset(id="id", name="name", owner="owner", source="source")
    print(asset)

    import base64
    from phcli.ph_db.ph_pg import PhPg

    pg = PhPg(
        base64.b64decode('cGgtZGItbGFtYmRhLmNuZ2sxamV1cm1udi5yZHMuY24tbm9ydGh3ZXN0LTEuYW1hem9uYXdzLmNvbS5jbgo=').decode('utf8')[:-1],
        base64.b64decode('NTQzMgo=').decode('utf8')[:-1],
        base64.b64decode('cGhhcmJlcnMK').decode('utf8')[:-1],
        base64.b64decode('QWJjZGUxOTYxMjUK').decode('utf8')[:-1],
        db=base64.b64decode('cGhlbnRyeQo=').decode('utf8')[:-1],
    )
    pg.insert(asset)
    pg.commit()
