from .db import PostDB
from .ocr_validator import OcrValidator


class ParkingLot():
    def __init__(self, user: str = 'postgres', password: str = 'password', database: str = 'parkinglot', table: str = 'entrances') -> None:
        db = PostDB(user=user, password=password)
        db.create_database(database=database)
        db.switch_connection(user=user, password=password, database=database)
        db.create_table(table=table)

    @staticmethod
    def check(img: str) -> str:
        license = OcrValidator.ocr(img)
        return OcrValidator.license_validator(license)
