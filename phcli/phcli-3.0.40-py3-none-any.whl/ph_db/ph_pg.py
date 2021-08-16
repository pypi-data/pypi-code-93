import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from phcli.ph_db.ph_db_api import PhDBAPI


class PhPg(PhDBAPI):
    def __init__(self, host, port, user, passwd, db):
        self.engine = None
        self.session = None

        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db

        self.engine = create_engine('postgresql://{user}:{passwd}@{host}:{port}/{db}'.format(**self.__dict__))
        Session = sessionmaker(bind=self.engine)
        self.session = Session()


if __name__ == '__main__':
    from phcli.ph_max_auto.ph_models.data_set import DataSet

    pg = PhPg(
        base64.b64decode('cGgtZGItbGFtYmRhLmNuZ2sxamV1cm1udi5yZHMuY24tbm9ydGh3ZXN0LTEuYW1hem9uYXdzLmNvbS5jbgo=').decode('utf8')[:-1],
        base64.b64decode('NTQzMgo=').decode('utf8')[:-1],
        base64.b64decode('cGhhcmJlcnMK').decode('utf8')[:-1],
        base64.b64decode('QWJjZGUxOTYxMjUK').decode('utf8')[:-1],
        db=base64.b64decode('cGhlbnRyeQo=').decode('utf8')[:-1],
    )

    print(pg.tables())

    # print(pg.insert(DataSet(job='job')))

    query = pg.query(DataSet(job="job"))
    for q in query:
        print(q)

    pg.commit()

