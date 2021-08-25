from hestia_earth.models.utils.impact_assessment import _get_impacts_dict, get_product, impact_value


def test_get_impacts_dict():
    impacts = _get_impacts_dict()
    assert len(impacts.keys()) > 0


def test_get_product():
    term_id = 'id'
    product = {
        'term': {'@id': term_id}
    }
    cycle = {'products': [product]}
    impact = {'product': {'@id': term_id}}

    # no product
    assert not get_product(impact)

    # with cycle and product
    impact['cycle'] = cycle
    assert get_product(impact) == product


def test_get_value():
    impact = {
        'emissionsResourceUse': [
            {
                'term': {
                    '@id': 'ch4ToAirSoil'
                },
                'value': 100
            }
        ]
    }
    # multiplies the emissionsResourceUse values with a coefficient
    assert impact_value(impact, 'co2EqGwp100ExcludingClimate-CarbonFeedbacksIpcc2013') == 2850
