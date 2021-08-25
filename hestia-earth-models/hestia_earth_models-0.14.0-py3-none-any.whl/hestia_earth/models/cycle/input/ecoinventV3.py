from hestia_earth.utils.model import linked_node

from hestia_earth.models.utils.impact_assessment import _get_impacts_dict
MODEL = 'ecoinventV3'


def _input(input: dict, impacts: dict):
    impact = impacts[input.get('term', {}).get('@id')]
    return {**input, 'impactAssessment': linked_node(impact)}


def run(cycle: dict):
    impacts = _get_impacts_dict()
    inputs = [i for i in cycle.get('inputs', []) if i.get('term', {}).get('@id') in impacts
              and not i.get('impactAssessment')]
    return [_input(i, impacts) for i in inputs]
