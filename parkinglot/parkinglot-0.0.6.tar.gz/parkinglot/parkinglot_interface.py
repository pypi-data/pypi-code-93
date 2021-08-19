from db import PostDB
from ocr_validator import OcrValidator


class ParkingLot():
    def __init__(self, user: str = 'postgres', password: str = 'password', database: str = 'parkinglot', table: str = 'entrances') -> None:
        db = PostDB
        db.create_database(database)
        db.switch_connection(user, password, database)
        db.create_table(table)

    @staticmethod
    def check(img: str) -> str:
        license = OcrValidator.ocr(img)
        return OcrValidator.license_validator(license)
