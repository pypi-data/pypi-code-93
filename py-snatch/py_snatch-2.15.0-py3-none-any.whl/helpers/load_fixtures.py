import json
from pathlib import Path
from typing import Any, Dict


def load_fixture(filename: str) -> Dict[Any, Any]:
    """Load fixtures from test/fixtures folder.

    Example:
    * Add the file `my_response.json` in tests/fixtures
    * In tests load the file using::

        >>> from snatch.helpers.load_fixtures import load_fixture

        >>> def test_load_fixure():
        >>>     data = load_fixture("my_response.json")
        >>>     assert data is not None

    :param filename: JSON Filename
    :return: Dict
    """
    file_path = Path.cwd().joinpath("tests", "fixtures", filename)
    with open(str(file_path), encoding="UTF-8") as file:
        fixture = json.load(file)
    return fixture
