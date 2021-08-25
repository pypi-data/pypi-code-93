from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_indicator

from hestia_earth.models.aware.scarcityWeightedWaterUse import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.aware.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/aware/{TERM_ID}"


@patch(f"{class_path}.find_term_match")
def test_should_run(mock_find_term_match):
    impact = {}

    # with an emission => no run
    mock_find_term_match.return_value = {
        'value': 100
    }
    should_run, *args = _should_run(impact)
    assert not should_run

    # with a cycle
    cycle = {}
    impact['cycle'] = cycle

    # with a site and awareWaterBasinId => no run
    cycle['site'] = {'awareWaterBasinId': '2424'}
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


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_site_cropland(*args):
    with open(f"{fixtures_folder}/with-site-cropland/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/with-site-cropland/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected


@patch(f"{class_path}._new_indicator", side_effect=fake_new_indicator)
def test_run_country(*args):
    with open(f"{fixtures_folder}/with-country/impact-assessment.jsonld", encoding='utf-8') as f:
        impact = json.load(f)

    with open(f"{fixtures_folder}/with-country/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(impact)
    assert value == expected
