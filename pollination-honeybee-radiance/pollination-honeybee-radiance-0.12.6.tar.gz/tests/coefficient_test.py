from pollination.honeybee_radiance.coefficient import DaylightCoefficient
from queenbee.plugin.function import Function


def test_daylight_coefficient():
    function = DaylightCoefficient().queenbee
    assert function.name == 'daylight-coefficient'
    assert isinstance(function, Function)
