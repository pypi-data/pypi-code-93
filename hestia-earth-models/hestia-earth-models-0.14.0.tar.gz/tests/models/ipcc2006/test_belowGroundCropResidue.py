from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.ipcc2006.belowGroundCropResidue import TERM_ID, run, _should_run

class_path = 'hestia_earth.models.ipcc2006.belowGroundCropResidue'
fixtures_folder = f"{fixtures_path}/ipcc2006/{TERM_ID}"


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}.find_primary_product")
def test_should_run(mock_primary_product, *args):
    # no primary product => no run
    mock_primary_product.return_value = None
    should_run, *args = _should_run({})
    assert not should_run

    # with primary product => run
    mock_primary_product.return_value = {'value': [10]}
    should_run, *args = _should_run({})
    assert should_run


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_koga(*args):
    with open(f"{fixtures_folder}/koga/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/koga/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_gap_fill_default(*args):
    with open(f"{fixtures_folder}/default-no-dm-property/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/default-no-dm-property/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
