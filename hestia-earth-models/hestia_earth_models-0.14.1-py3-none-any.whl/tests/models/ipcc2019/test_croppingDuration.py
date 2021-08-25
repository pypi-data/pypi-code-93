from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_practice

from hestia_earth.models.ipcc2019.croppingDuration import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.ipcc2019.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/ipcc2019/{TERM_ID}"


@patch(f"{class_path}.get_table_value", return_value='0')
def test_should_run(*args):
    # no cycleDuration => no run
    cycle = {}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # no site => no run
    cycle = {'cycleDuration': 100, 'site': {}}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with site => run
    cycle['site'] = {'country': {'@id': 'country'}}
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


@patch(f"{class_path}._new_practice", side_effect=fake_new_practice)
def test_run_sup_cycleDuration(*args):
    with open(f"{fixtures_folder}/sup-cycleDuration/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    value = run(cycle)
    assert value == []
