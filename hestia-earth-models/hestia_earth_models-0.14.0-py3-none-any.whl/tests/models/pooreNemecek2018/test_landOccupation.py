from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator
from hestia_earth.schema import CycleFunctionalUnit

from hestia_earth.models.pooreNemecek2018.landOccupation import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.pooreNemecek2018.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/pooreNemecek2018/{TERM_ID}"


@patch(f"{class_path}.get_product", return_value=None)
def test_should_run(mock_get_product):
    # with a cycle and functionalUnit = 1 ha => no run
    impact = {'cycle': {'functionalUnit': CycleFunctionalUnit._1_HA.value}}
    should_run, *args = _should_run(impact)
    assert not should_run

    # with product value and economicValueShare => run
    mock_get_product.return_value = {'value': [10], 'economicValueShare': 80, 'term': {'@id': 'product'}}
    should_run, *args = _should_run(impact)
    assert should_run is True


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run(*args):
    with open(f"{fixtures_folder}/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_fallow_correction(*args):
    with open(f"{fixtures_folder}/with-fallowCorrection/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/with-fallowCorrection/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
