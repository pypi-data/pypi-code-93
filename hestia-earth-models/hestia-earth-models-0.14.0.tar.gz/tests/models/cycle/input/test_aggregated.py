from unittest.mock import patch
import json

from hestia_earth.schema import TermTermType

from tests.utils import fixtures_path
from hestia_earth.models.cycle.input.aggregated import MODEL, run, _should_run, _should_run_seed

class_path = f"hestia_earth.models.cycle.input.{MODEL}"
fixtures_folder = f"{fixtures_path}/cycle/input/{MODEL}"

IMPACT_ASSESSMENT = {
    "@id": "wheatGrain-australia-2001-2010",
    "@type": "ImpactAssessment",
    "name": "Wheat, grain, Australia, 2001-2010"
}


def test_should_run():
    cycle = {}

    # no inputs => no run
    cycle['inputs'] = []
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with inputs and no impactAssessment => no run
    cycle['inputs'] = [{}]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with country => no run
    cycle['site'] = {'country': 'GADM-AUS'}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with endDate => run
    cycle['endDate'] = {'2019'}
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.find_primary_product", return_value={})
def test_should_run_seed(mock_primary_product, *args):
    cycle = {}

    # with a crop product => no run
    mock_primary_product.return_value = {'term': {'termType': TermTermType.CROP.value}}
    should_run, *args = _should_run_seed(cycle)
    assert not should_run

    # with a seed input => run
    cycle['inputs'] = [{'term': {'@id': 'seed'}}]
    should_run, *args = _should_run_seed(cycle)
    assert should_run is True


@patch(f"{class_path}.search", return_value=[IMPACT_ASSESSMENT])
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}.search", return_value=[IMPACT_ASSESSMENT])
def test_run_seed(*args):
    with open(f"{fixtures_folder}/seed/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/seed/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
