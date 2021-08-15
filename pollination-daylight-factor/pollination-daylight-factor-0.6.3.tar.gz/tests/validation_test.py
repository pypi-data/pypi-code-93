from pollination.daylight_factor.entry import DaylightFactorEntryPoint
from queenbee.recipe.dag import DAG


def test_daylight_factor():
    recipe = DaylightFactorEntryPoint().queenbee
    assert recipe.name == 'daylight-factor-entry-point'
    assert isinstance(recipe, DAG)
