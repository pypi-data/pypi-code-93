import ocrspace
import regex as re

from .config import api_key
from .db import PostDB
from .utils import logger

# Instance of PostDB for insertion of data
db_insert = PostDB.insert_data


class ENUM():
    ALLOWED = 'ALLOWED'
    NOT_ALLOWED = 'NOT_ALLOWED'
    NOT_VALID = 'NOT_VALID'


class OcrValidator():
    @staticmethod
    def ocr(file: str) -> str:
        """
        :params: file as a path string
        :return: str (License plate number)
        """
        api = ocrspace.API(
            endpoint='https://api.ocr.space/parse/image', api_key=api_key)
        try:
            filename = file

            # A fixed list of strings without any whitespaces charecters
            result = api.ocr_file(open(filename, 'rb')).splitlines()

            # Return the first the first element or an empty string if list is empty
            return result[0] if result != [] else ''

        except Exception as e:
            logger.warning(e, exc_info=True)
            raise Exception(
                "There is something wrong with the api please check log for farther understanding")

    @staticmethod
    def license_validator(license: str) -> str:
        """:return: ALLOWED/NOT_ALLOWED/NOT_VALID to enter the parking lot"""

        logger.info(f'Function is_allowed is running with {license = }')

        state = ENUM.ALLOWED

        try:
            # Check if there is any (non-digit || non-letter) in license charecters
            if re.sub(r'[a-zA-Z0-9]', '', license):
                state = ENUM.NOT_VALID
                return state

            # Check if last charecter in license is 6 or G
            if license[-1] in ('6', 'G'):
                state = ENUM.NOT_ALLOWED
                db_insert(license, state)
                return state

            # Check rather there is ('L' || 'M') in license charecters
            if 'L' in license or 'M' in license:
                state = ENUM.NOT_ALLOWED
                db_insert(license, state)
                return state

            # Check if license charecters are all digits
            if False not in map(str.isdigit, license):
                state = ENUM.NOT_ALLOWED
                db_insert(license, state)
                return state

        except Exception as err:
            logger.warning(
                f'License is an empty string! \n{str(err)}', exc_info=True)
            state = ENUM.NOT_VALID
            return state

        finally:
            logger.info(
                f'Function is_allowed done checking {license = } with status: {state}')

        db_insert(license, state)
        return state
