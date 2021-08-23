from pollination.honeybee_radiance.post_process import ConvertToBinary, SumRow, \
    AnnualIrradianceMetrics, AnnualDaylightMetrics, LeedIlluminanceCredits

from queenbee.plugin.function import Function


def test_convert_to_binary():
    function = ConvertToBinary().queenbee
    assert function.name == 'convert-to-binary'
    assert isinstance(function, Function)


def test_sum_row():
    function = SumRow().queenbee
    assert function.name == 'sum-row'
    assert isinstance(function, Function)


def test_annual_irradiance_metrics():
    function = AnnualIrradianceMetrics().queenbee
    assert function.name == 'annual-irradiance-metrics'
    assert isinstance(function, Function)


def test_annual_daylight_metrics():
    function = AnnualDaylightMetrics().queenbee
    assert function.name == 'annual-daylight-metrics'
    assert isinstance(function, Function)


def test_leed_illuminance_credits():
    function = LeedIlluminanceCredits().queenbee
    assert function.name == 'leed-illuminance-credits'
    assert isinstance(function, Function)
