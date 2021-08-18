import regex as re

from db import db_insert
from utils import logger, now


def is_allowed(license: str) -> str:
    """:return: ALLOWED/NOT_ALLOWED/NOT_VALID to enter the parking lot"""

    logger.info(f'Function is_allowed is running with {license = }')

    enum = ['ALLOWED', 'NOT_ALLOWED', 'NOT_VALID']
    state = enum[0]

    try:
        # Check if there is any (non-digit || non-letter) in license charecters
        if re.sub(r'[a-zA-Z0-9]', '', license):
            state = enum[2]
            return state

        # Check if last charecter in license is 6 or G
        if license[-1] in ('6', 'G'):
            state = enum[1]
            db_insert(license, state)
            return state

        # Check rather there is ('L' || 'M') in license charecters
        if 'L' in license or 'M' in license:
            state = enum[1]
            db_insert(license, state)
            return state

        # Check if license charecters are all digits
        if False not in [*map(str.isdigit, license)]:
            state = enum[1]
            db_insert(license, state)
            return state

    except Exception as err:
        logger.warning(
            f'License is an empty string! \n{str(err)}', exc_info=True)
        state = enum[2]
        return state

    finally:
        logger.info(
            f'Function is_allowed done checking {license = } with status: {state}')

    db_insert(license, state)
    return state


def main():
    pass


if __name__ == '__main__':
    main()
