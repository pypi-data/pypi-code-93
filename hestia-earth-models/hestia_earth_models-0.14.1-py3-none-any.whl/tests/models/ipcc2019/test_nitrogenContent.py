from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_property

from hestia_earth.models.ipcc2019.nitrogenContent import MODEL, TERM_ID, _should_run, _should_run_product, run

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"


def test_should_run():
    cycle = {'products': []}

    # no products => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with primary product => no run
    cycle['products'] = [{'primary': True}]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with related product => run
    cycle['products'].append({'term': {'@id': 'belowGroundCropResidue'}})
    should_run, *args = _should_run(cycle)
    assert should_run is True


def test_should_run_product():
    product = {}

    # not a runed product => no run
    product['term'] = {'@id': 'random id'}
    assert not _should_run_product(product)

    # with a runed product => run
    product['term']['@id'] = 'aboveGroundCropResidueTotal'
    assert _should_run_product(product) is True

    prop = {
        'term': {
            '@id': TERM_ID
        }
    }
    product['properties'] = [prop]
    assert not _should_run_product(product)


@patch(f"{class_path}._new_property", side_effect=fake_new_property)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
