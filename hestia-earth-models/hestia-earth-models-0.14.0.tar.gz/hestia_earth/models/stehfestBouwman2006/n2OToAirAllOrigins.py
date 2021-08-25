from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
import numpy as np
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value
from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logger, debugRequirements
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.input import get_total_nitrogen
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'n2OToAirAllOrigins'
N2O_FACTORS_BY_CROP = {
    'Cereals': 0,
    'Grass': -0.3502,
    'Legume': 0.3783,
    'Other': 0.4420,
    'W-Rice': -0.8850,
    'None': 0.5870
}


def _get_crop_crouping(product: dict):
    term_id = product.get('term', {}).get('@id') if product else None
    lookup = download_lookup('crop.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name('cropGroupingStehfestBouwman'))


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    clay = most_relevant_measurement_value(measurements, 'clayContent', end_date)
    sand = most_relevant_measurement_value(measurements, 'sandContent', end_date)
    organicCarbonContent = most_relevant_measurement_value(measurements, 'organicCarbonPerKgSoil', end_date)
    soilPh = most_relevant_measurement_value(measurements, 'soilPh', end_date)
    ecoClimateZone = most_relevant_measurement_value(measurements, 'ecoClimateZone', end_date)
    product = find_primary_product(cycle)
    crop_grouping = _get_crop_crouping(product) if product else None
    N_total = list_sum(get_total_nitrogen(cycle.get('inputs', [])))
    content_list_of_items = [clay, sand, organicCarbonContent, soilPh, ecoClimateZone, crop_grouping]

    debugRequirements(model=MODEL, term=TERM_ID,
                      clay=clay,
                      sand=sand,
                      organicCarbonContent=organicCarbonContent,
                      soilPh=soilPh,
                      ecoClimateZone=ecoClimateZone,
                      crop_grouping=crop_grouping)

    should_run = valid_site_type(cycle) \
        and all(content_list_of_items) \
        and N_total > 0 \
        and crop_grouping in N2O_FACTORS_BY_CROP
    return should_run, N_total, content_list_of_items


def _organic_carbon_factor(organicCarbonContent: float):
    return 0 if organicCarbonContent < 10 else (0.0526 if organicCarbonContent <= 3 else 0.6334)


def _soilph_factor(soilPh: float):
    return 0 if soilPh < 5.5 else (-0.4836 if soilPh > 7.3 else -0.0693)


def _sand_factor(sand: float, clay: float):
    return 0 if sand > 65 and clay < 18 else (-0.1528 if sand < 65 and clay < 35 else 0.4312)


def _get_value(content_list_of_items: list, N_total: float):
    clay, sand, organicCarbonContent, soilPh, ecoClimateZone, crop_grouping = content_list_of_items

    carbon_factr = _organic_carbon_factor(organicCarbonContent)
    soil_factr = _soilph_factor(soilPh)
    sand_factr = _sand_factor(sand, clay)
    eco_factor = get_ecoClimateZone_lookup_value(ecoClimateZone, 'STEHFEST_BOUWMAN_2006_N2O-N_FACTOR')
    crop_grp_factor = N2O_FACTORS_BY_CROP[crop_grouping]
    factors_sum = sum([carbon_factr, soil_factr, sand_factr, eco_factor, crop_grp_factor])

    value = np.amin(((
        0.072 * N_total,
        np.exp(0.475 + 0.0038 * N_total + factors_sum) - np.exp(0.475 + factors_sum))
    )) * get_atomic_conversion(Units.KG_N2O, Units.TO_N)
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)

    return value


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(content_list_of_items: list, N_total: float):
    value = _get_value(content_list_of_items, N_total)
    return [_emission(value)]


def run(cycle: dict):
    should_run, N_total, content_list_of_items = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(content_list_of_items, N_total) if should_run else []
