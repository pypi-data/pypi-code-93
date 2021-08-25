import math
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import search
from hestia_earth.utils.model import find_primary_product, find_term_match, linked_node
from hestia_earth.utils.tools import non_empty_list, safe_parse_date

from hestia_earth.models.log import logger
from hestia_earth.models.utils.cycle import is_organic, is_irrigated, valid_site_type
MODEL = 'aggregated'
MODEL_KEY = 'impactAssessment'
SEED_TERM_ID = 'seed'


def _name_suffix(cycle: dict):
    return '-'.join(non_empty_list([
        'Organic' if is_organic(cycle) else 'Conventional',
        'Irrigated' if is_irrigated(cycle) else 'Non Irrigated'
    ]))


def _end_date(end_date: str):
    year = safe_parse_date(end_date).year
    return round((math.floor(year / 10) + 1) * 10)


def _find_closest_impact(cycle: dict, country: dict, end_date: str, input: dict):
    query = {
        'bool': {
            'must': [
                {'match': {'@type': SchemaType.IMPACTASSESSMENT.value}},
                {'match': {'aggregated': 'true'}},
                {'match': {'product.name.keyword': input.get('term', {}).get('name')}},
                {
                    'bool': {
                        # either get with exact country, or default to global
                        'should': [
                            {'match': {'country.name.keyword': {'query': country.get('name'), 'boost': 1000}}},
                            {'match': {'country.name.keyword': {'query': 'World', 'boost': 1}}}
                        ],
                        'minimum_should_match': 1
                    }
                }
            ],
            'should': [
                {'match': {'name': _name_suffix(cycle)}},
                {'match': {'endDate': _end_date(end_date)}}
            ]
        }
    }
    results = search(query)
    result = results[0] if len(results) > 0 else {}
    logger.debug('found aggregated impact for term=%s: %s', input.get('term', {}).get('@id'), result.get('@id'))
    return result


def _run_seed(cycle: dict, product: dict, input: dict, country: dict, end_date: str):
    impact = _find_closest_impact(cycle, country, end_date, product)
    return [{**input, MODEL_KEY: linked_node(impact)}] if impact else []


def _should_run_seed(cycle: dict):
    primary_product = find_primary_product(cycle)
    term_type = primary_product.get('term', {}).get('termType') if primary_product else None
    input = find_term_match(cycle.get('inputs', []), SEED_TERM_ID, None)
    should_run = term_type == TermTermType.CROP.value and input is not None and valid_site_type(cycle, True)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, SEED_TERM_ID, should_run)
    return should_run, primary_product, input


def _run(cycle: dict, inputs: list, country: dict, end_date: str):
    inputs = [
        {**i, MODEL_KEY: linked_node(_find_closest_impact(cycle, country, end_date, i))} for i in inputs
    ]
    return list(filter(lambda i: i.get(MODEL_KEY).get('@id') is not None, inputs))


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    country = cycle.get('site', {}).get('country')
    # do not override inputs that already have an impactAssessment
    inputs = [i for i in cycle.get('inputs', []) if not i.get(MODEL_KEY)]

    should_run = end_date is not None and country is not None and len(inputs) > 0
    logger.info('model=%s, should_run=%s', MODEL, should_run)
    return should_run, inputs, country, end_date


def run(cycle: dict):
    should_run, inputs, country, end_date = _should_run(cycle)
    should_run_seed, primary_product, seed_input = _should_run_seed(cycle)
    return _run(cycle, inputs, country, end_date) + (
        _run_seed(cycle, primary_product, seed_input, country, end_date) if should_run_seed else []
    ) if should_run else []
