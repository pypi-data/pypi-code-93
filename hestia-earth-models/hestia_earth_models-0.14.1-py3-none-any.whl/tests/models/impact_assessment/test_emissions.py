import json
from unittest.mock import patch
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.impact_assessment.emissions import run, _should_run

class_path = 'hestia_earth.models.impact_assessment.emissions'
fixtures_folder = f"{fixtures_path}/impact_assessment/emissions"


@patch(f"{class_path}.get_product")
def test_should_run(mock_get_product):
    product = {}
    mock_get_product.return_value = product

    # no economicValueShare => no run
    should_run, *args = _should_run({})
    assert not should_run

    # with economicValueShare => not run
    product['economicValueShare'] = 50
    should_run, *args = _should_run({})
    assert not should_run

    # with yield => run
    product['value'] = [50]
    should_run, *args = _should_run({})
    assert should_run


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
