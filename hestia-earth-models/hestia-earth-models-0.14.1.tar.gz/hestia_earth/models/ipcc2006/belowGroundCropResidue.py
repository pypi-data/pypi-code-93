from hestia_earth.schema import ProductStatsDefinition
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.lookup import get_table_value, download_lookup
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.product import _new_product
from hestia_earth.models.utils.property import get_node_property
from . import MODEL

TERM_ID = 'belowGroundCropResidue'
PROPERTY_KEY = 'dryMatter'


def _get_value_default(primary_product: dict):
    lookup = download_lookup('crop.csv', True)

    term_id = primary_product.get('term', {}).get('@id', '')
    in_lookup = term_id in list(lookup.termid)
    logger.debug('Found lookup data for Term: %s? %s', term_id, in_lookup)

    return safe_parse_float(
        get_table_value(lookup, 'termid', term_id, 'default_bg_dm_crop_residue'), None
    ) if in_lookup else None


def _get_value_dm(term_id: str, primary_product_yield: int, dm_percent: float):
    lookup = download_lookup('crop.csv', True)

    in_lookup = term_id in list(lookup.termid)
    logger.debug('Found lookup data for Term: %s? %s', term_id, in_lookup)

    if in_lookup:
        # Multiply yield by dryMatter proportion
        yield_dm = primary_product_yield * (dm_percent / 100)
        # TODO with the spreadsheet there are a number of ways this value is calculated.
        # Currently, the result of this model when applied to Sah et al does not match
        # the example due to hardcoded calc in the spreadsheet

        # estimate the BG DM calculation
        bg_slope = safe_parse_float(
            get_table_value(lookup, 'termid', term_id, 'crop_residue_slope')
        )
        bg_intercept = safe_parse_float(
            get_table_value(lookup, 'termid', term_id, 'crop_residue_intercept')
        )
        ab_bg_ratio = safe_parse_float(
            get_table_value(lookup, 'termid', term_id, 'ratio_abv_to_below_grou_crop_residue')
        )

        above_ground_residue = yield_dm * bg_slope + bg_intercept * 1000

        # TODO: Update to include fraction renewed addition of
        #  https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch11_Soils_N2O_CO2.pdf
        #  only if site.type = pasture
        # multiply by the ratio of above to below matter
        return None if bg_slope is None or bg_intercept is None or ab_bg_ratio is None \
            else (above_ground_residue + yield_dm) * ab_bg_ratio
    return None


def _product(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    product = _new_product(TERM_ID, MODEL)
    product['value'] = [value]
    product['statsDefinition'] = ProductStatsDefinition.MODELLED.value
    return product


def _run(primary_product: dict):
    dm_property = get_node_property(primary_product, PROPERTY_KEY)
    term_id = primary_product.get('term', {}).get('@id')

    #  1) use dm regression, or 2) use default for orchard crops
    value = _get_value_dm(
        term_id, list_sum(primary_product.get('value')), safe_parse_float(dm_property.get('value'))
    ) if dm_property else _get_value_default(primary_product)

    return [_product(value)] if value is not None else []


def _should_run(cycle: dict):
    product = find_primary_product(cycle) or {}
    product_value = list_sum(product.get('value', []))

    debugRequirements(model=MODEL, term=TERM_ID,
                      product_value=product_value)

    should_run = product_value > 0 and _is_term_type_incomplete(cycle, TERM_ID)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, product


def run(cycle: dict):
    should_run, primary_product = _should_run(cycle)
    return _run(primary_product) if should_run else []
