from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_product

from hestia_earth.models.ipcc2006.aboveGroundCropResidueTotal import TERM_ID, run, _should_run

class_path = 'hestia_earth.models.ipcc2006.aboveGroundCropResidueTotal'
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
def test_run_removed_practice_product(*args):
    with open(f"{fixtures_folder}/with-removed-practive-and-product/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-removed-practive-and-product/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_removed_product(*args):
    with open(f"{fixtures_folder}/with-removed-product/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-removed-product/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_run_removed_practice(*args):
    with open(f"{fixtures_folder}/with-removed-practice/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-removed-practice/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._is_term_type_incomplete", return_value=True)
@patch(f"{class_path}._new_product", side_effect=fake_new_product)
def test_gap_fill_tree_nut(*args):
    with open(f"{fixtures_folder}/default-no-dm-property/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/default-no-dm-property/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
