import ocrspace
from ocrspace.main import Language

from config import api_key
from utils import logger


def ocr(file: str) -> str:
    """
    :params: file as a path string
    :return: str (License plate number)
    """
    api = ocrspace.API(
        endpoint='https://api.ocr.space/parse/image', api_key=api_key)
    try:
        filename = file

        result = api.ocr_file(open(filename, 'rb')).splitlines()

        return result[0] if result != [] else ''

    except Exception as e:
        logger.warning(e, exc_info=True)
        raise Exception(
            "There is something wrong with the api please check log for farther understanding")
