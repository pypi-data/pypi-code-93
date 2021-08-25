from unittest.mock import patch
import json
from tests.utils import fixtures_path, fake_new_emission

from hestia_earth.models.ipcc2019.ch4ToAirExcreta import TERM_ID, run, _should_run

class_path = f"hestia_earth.models.ipcc2019.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/ipcc2019/{TERM_ID}"


@patch(f"{class_path}._get_ch4_conv_factor", return_value=None)
@patch(f"{class_path}._get_ch4_potential", return_value=None)
def test_should_run(mock_ch4_potential, mock_ch4_conv):
    cycle = {'practices': []}

    # no practices => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    cycle = {'products': []}

    # no products => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    cycle = {'inputs': []}

    # no inputs => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    cycle = {
             'site': {
                 'measurements': []
             }
    }

    # no measurements, => no run
    should_run, *args = _should_run(cycle)
    assert not should_run

    mock_ch4_potential.return_value = 10
    mock_ch4_conv.return_value = 10
    cycle = {
        'inputs': [
            {
                'term': {
                    '@id': 'excretaKgVs',
                    'termType': 'excreta',
                    'units': 'kg VS'
                },
                'value': [
                    10
                ]
            }
        ]
    }

    # with excretaKgVs => run
    should_run, *args = _should_run(cycle)
    assert should_run


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
