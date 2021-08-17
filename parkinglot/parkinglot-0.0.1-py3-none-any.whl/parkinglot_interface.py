import db
from is_allowed import is_allowed
from ocr_api import ocr


class ParkingLot():
    def __init__(self, user: str = 'postgres', password: str = 'password') -> None:
        cur = db.db_establish_connection(user, password)
        db.db_create_database(cur)
        db.db_create_table(database='parkinglot')

    @staticmethod
    def check(img: str) -> str:
        license = ocr(img)
        return is_allowed(license)

    @staticmethod
    def db_insert(license: str, status: str):
        db.db_insert(license, status)


def main():
    pass


if __name__ == '__main__':
    main()
