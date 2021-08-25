from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.impact_assessment.freshwaterWithdrawals import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.impact_assessment.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/impact_assessment/{TERM_ID}"


@patch(f"{class_path}.get_product", return_value=None)
def test_should_run(mock_product):
    impact = {}

    # with a product economicValueShare + value => no run
    mock_product.return_value = {
        'economicValueShare': 10,
        'value': [100]
    }
    should_run, *args = _should_run(impact)
    assert not should_run

    # with a cycle
    cycle = {}
    impact['cycle'] = cycle

    # with water => run
    cycle['inputs'] = [{
        'term': {'termType': 'water'},
        'value': [10]
    }]
    should_run, *args = _should_run(impact)
    assert should_run


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
