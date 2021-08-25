from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.ch4ToAirFloodedRice import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.ipcc2019.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/ipcc2019/{TERM_ID}"


def test_should_run():
    # no site => no run
    cycle = {'site': {}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with site => no run
    cycle['site'] = {'country': {'@id': 'country'}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with flooded rice => no run
    cycle['products'] = [{'term': {'@id': 'riceGrainPaddy'}}]
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with croppingDuration => run
    cycle['practices'] = [{'term': {'@id': 'croppingDuration'}}]
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run_with_optional_data(*args):
    with open(f"{fixtures_folder}/with-optional-data/cycle.jsonld", encoding="utf-8") as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/with-optional-data/result.jsonld", encoding="utf-8") as f:
        expected = json.load(f)

    result = run(cycle)
    assert result == expected
