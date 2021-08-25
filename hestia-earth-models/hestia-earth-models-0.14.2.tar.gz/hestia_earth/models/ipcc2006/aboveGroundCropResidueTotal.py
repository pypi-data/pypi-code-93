from hestia_earth.schema import ProductStatsDefinition
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.lookup import get_table_value, download_lookup
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from . import MODEL
from hestia_earth.models.koble2014.residue.residueRemoved import TERM_ID as PRACTICE_TERM_ID
from .aboveGroundCropResidueRemoved import TERM_ID as REMOVED_TERM_ID

TERM_ID = 'aboveGroundCropResidueTotal'
PROPERTY_KEY = 'dryMatter'


def _get_removed_practice_value(cycle: dict) -> float:
    value = find_term_match(cycle.get('practices', []), PRACTICE_TERM_ID).get('value', [])
    return list_sum(value) / 100 if len(value) > 0 else None


def _get_value_default(primary_product: dict):
    lookup = download_lookup('crop.csv', True)

    term_id = primary_product.get('term', {}).get('@id', '')
    in_lookup = term_id in list(lookup.termid)
    logger.debug('Found lookup data for Term: %s? %s', term_id, in_lookup)

    return safe_parse_float(
        get_table_value(lookup, 'termid', term_id, 'default_ag_dm_crop_residue'), None
    ) if in_lookup else None


def _get_value_dm(primary_product: dict, dm_percent: float):
    lookup = download_lookup('crop.csv', True)

    term_id = primary_product.get('term', {}).get('@id', '')
    product_yield = primary_product.get('value', [0])[0]

    in_lookup = term_id in list(lookup.termid)
    logger.debug('Found lookup data for Term: %s? %s', term_id, in_lookup)

    if in_lookup:
        # Multiply yield by dryMatter proportion
        yield_dm = product_yield * (dm_percent / 100)

        # estimate the AG DM calculation
        ag_slope = safe_parse_float(
            get_table_value(lookup, 'termid', term_id, 'crop_residue_slope'), None
        )
        ag_intercept = safe_parse_float(
            get_table_value(lookup, 'termid', term_id, 'crop_residue_intercept'), None
        )
        logger.debug('term=%s, yield=%s, dry_matter_percent=%s, slope=%s, intercept=%s',
                     term_id, product_yield, dm_percent, ag_slope, ag_intercept)

        # estimate abv. gro. residue as dry_yield * slope + intercept * 1000.  IPCC 2006 (Poore & Nemecek 2018)
        return None if ag_slope is None or ag_intercept is None else (yield_dm * ag_slope + ag_intercept * 1000)

    return None


def _product(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    product = _new_product(TERM_ID, MODEL)
    product['value'] = [value]
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _run(cycle: dict, primary_product: dict):
    removed_practice_value = _get_removed_practice_value(cycle)
    dm_property = get_node_property(primary_product, PROPERTY_KEY) if primary_product is not None else None
    removed_value = _get_removed_value(cycle)

    #  1) gap-fill using removed amount and practice value, or 2) use dm regression, or 3) use default for orchard crops
    value = 0 if removed_value and removed_practice_value == 0 else \
        removed_value / removed_practice_value if removed_value and removed_practice_value else \
        _get_value_dm(primary_product, safe_parse_float(dm_property.get('value'))) if dm_property else \
        _get_value_default(primary_product)

    return [_product(value)] if value is not None else []


def _get_removed_value(cycle: dict):
    # if we find the removed value, we can infer the total
    value = find_term_match(cycle.get('products', []), REMOVED_TERM_ID).get('value', [])
    return list_sum(value)


def _should_run(cycle: dict):
    product = find_primary_product(cycle) or {}
    product_value = list_sum(product.get('value', []))

    debugRequirements(model=MODEL, term=TERM_ID,
                      product_value=product_value)

    should_run = product_value > 0 and _is_term_type_incomplete(cycle, TERM_ID)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, product


def run(cycle: dict):
    should_run, product = _should_run(cycle)
    return _run(cycle, product) if should_run else []
