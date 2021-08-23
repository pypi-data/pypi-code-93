import json
import sys
from pathlib import Path

from pact_testgen.models import Pact


def load_pact_file(path: str) -> Pact:
    """Loads the file at the supplied path into a Pact model"""
    with open(Path(path), "r") as f:
        pact = json.load(f)
        return Pact(**pact)


def write_test_file(testfile: str, path: Path):
    with open(path, "w") as f:
        f.write(testfile)


def write_provider_state_file(provider_state_file: str, path: Path):
    # TODO: Support appending new provider state functions.
    # For now, don't write the file if it already exists
    if not path.exists():
        with open(path, "w") as f:
            f.write(provider_state_file)
    else:
        print("provider_states.py already exists, not overwriting.", file=sys.stderr)
