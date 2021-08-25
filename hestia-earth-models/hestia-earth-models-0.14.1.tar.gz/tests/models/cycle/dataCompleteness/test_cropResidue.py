from unittest.mock import patch
import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.dataCompleteness.cropResidue import run, MODEL_KEY

class_path = f"hestia_earth.models.cycle.dataCompleteness.{MODEL_KEY}"


@patch(f"{class_path}.find_node")
def test_run(mock_find_node):
    with open(f"{fixtures_path}/cycle/dataCompleteness/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    mock_find_node.return_value = [{'@id': 'aboveGroundCropResidueRemoved'}]
    assert run(cycle)

    mock_find_node.return_value = [{'@id': 'unknown-term'}]
    assert not run(cycle)
