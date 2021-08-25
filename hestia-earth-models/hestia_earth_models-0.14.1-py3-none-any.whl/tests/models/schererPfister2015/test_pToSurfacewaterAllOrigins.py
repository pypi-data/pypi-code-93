import json
from unittest.mock import patch

from hestia_earth.models.schererPfister2015.pToSurfacewaterAllOrigins import TERM_ID, _should_run, run
from tests.utils import fake_new_emission, fixtures_path

class_path = f"hestia_earth.models.schererPfister2015.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/schererPfister2015/{TERM_ID}"


@patch(f"{class_path}.valid_site_type", return_value=True)
@patch(f"{class_path}.most_relevant_measurement_value", return_value=0)
@patch(f"{class_path}.get_inorganic_fertilizer_P_total", return_value=0)
def test_should_run(mock_inorg_p_total, mock_measurement, _m):
    # no measurements => no run
    cycle = {'measurements': []}
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with slope => no run
    mock_measurement.return_value = 10
    should_run, *args = _should_run(cycle)
    assert not should_run

    # with inorganic P => run
    mock_inorg_p_total.return_value = 1
    should_run, *args = _should_run(cycle)
    assert should_run is True


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
def test_run(*args):
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
