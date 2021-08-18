from parkinglot.db import main
import db
from ocr_validator import OcrValidator


class ParkingLot():
    def __init__(self, user: str = 'postgres', password: str = 'password') -> None:
        cur = db.db_establish_connection(user, password)
        db.db_create_database(cur)
        db.db_create_table(database='parkinglot')

    @staticmethod
    def check(img: str) -> str:
        license = OcrValidator.ocr(img)
        return OcrValidator.license_validator(license)

    @staticmethod
    def db_insert(license: str, status: str):
        db.db_insert(license, status)
