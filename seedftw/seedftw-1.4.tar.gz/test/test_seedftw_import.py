from seedftw.exceptions import MovedToPlotneat
import pytest


def test_import():
    import seedftw

    seedftw.load_configuration()
    assert isinstance(seedftw.__version__, str)


def test_moved():
    from seedftw.visual import figure, plot
    from seedftw.exceptions import MovedToSenasopt
    from seedftw.energy.energy_asset import (
        wind_turbine_generator,
        solar_pv_generator,
        battery_optimal_controller,
    )

    # Plotneat
    with pytest.raises(MovedToPlotneat):
        figure.group_legend_by_name()
    with pytest.raises(MovedToPlotneat):
        figure.clean_legend()
    with pytest.raises(MovedToPlotneat):
        figure.minimalistic_show()

    # Senasopt
    with pytest.raises(MovedToPlotneat):
        plot.duration_curve()
    with pytest.raises(MovedToSenasopt):
        wind_turbine_generator()
    with pytest.raises(MovedToSenasopt):
        solar_pv_generator()
    with pytest.raises(MovedToSenasopt):
        battery_optimal_controller()
