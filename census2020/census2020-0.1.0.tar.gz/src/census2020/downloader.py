import tempfile
import time
from pathlib import Path
from urllib.parse import urljoin

import pyarrow as pa
import requests
import us

from census2020.parsers import parse_all

BASE_URL = "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/"


def get_state(state: str, max_attempts: int = 3) -> pa.Table:
    """
    Download the data for a specific state and parse it into a pyarrow Table

    Args:
        state: The name of the state (can be an abbreviation or full name)
        max_attempts: The maximum number of attempts to pull the data from the Census

    Returns:
        A pyarrow Table with the combined data
    """
    state_obj = us.states.lookup(state)
    if not state_obj:
        raise ValueError(f"Do not recognize state {state}")

    url = urljoin(BASE_URL, f'{state_obj.name.replace(" ", "_")}/')
    filename = f"{state_obj.abbr.lower()}2020.pl.zip"
    url = urljoin(url, filename)

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        num_attempts = 0
        while num_attempts < max_attempts:
            with requests.get(url, stream=True) as response:
                if not response.ok:
                    num_attempts += 1
                    time.sleep(3)
                    continue

                with open(tmpdir / filename, "wb") as outfile:
                    for chunk in response.iter_content(chunk_size=8192):
                        outfile.write(chunk)
                break

        if num_attempts == max_attempts:
            raise EnvironmentError(f"Ran out of attempts to download {state} data")

        # Now parse the data
        return parse_all(tmpdir / filename)
