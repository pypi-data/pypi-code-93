from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.chaudharyEtAl2015.biodiversityLossLandTransformation import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.chaudharyEtAl2015.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/chaudharyEtAl2015/{TERM_ID}"


@patch(f"{class_path}.get_region_factor", return_value=None)
@patch(f"{class_path}.find_term_match")
def test_should_run(mock_find_term_match, mock_get_factor):
    # missing emissions => no run
    mock_find_term_match.return_value = {}
    should_run, *args = _should_run({})
    assert not should_run

    # with emissions => no run
    mock_find_term_match.return_value = {'value': 10}
    should_run, *args = _should_run({})
    assert not should_run

    # with factors => run
    mock_get_factor.return_value = 10
    should_run, *args = _should_run({})
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
def test_run_with_ecoregion(*args):
    with open(f"{fixtures_folder}/with-ecoregion/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/with-ecoregion/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
