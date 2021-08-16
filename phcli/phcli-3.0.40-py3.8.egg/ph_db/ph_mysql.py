import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from phcli.ph_db.ph_db_api import PhDBAPI


class PhMysql(PhDBAPI):
    def __init__(self, host, port, user, passwd, db):
        self.engine = None
        self.session = None

        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db

        self.engine = create_engine('mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}'.format(**self.__dict__))
        Session = sessionmaker(bind=self.engine)
        self.session = Session()


if __name__ == '__main__':
    ms = PhMysql(
        host=base64.b64decode('cGgtZHctaW5zLWNsdXN0ZXIuY2x1c3Rlci1jbmdrMWpldXJtbnYucmRzLmNuLW5vcnRod2VzdC0xLmFtYXpvbmF3cy5jb20uY24K').decode('utf8')[:-1],
        port=base64.b64decode('MzMwNgo=').decode('utf8')[:-1],
        user=base64.b64decode('cGhhcmJlcnMK').decode('utf8')[:-1],
        passwd=base64.b64decode('QWJjZGUxOTYxMjUK').decode('utf8')[:-1],
        db=base64.b64decode('YWlyZmxvdwo=').decode('utf8')[:-1],
    )

    print(ms.tables())

