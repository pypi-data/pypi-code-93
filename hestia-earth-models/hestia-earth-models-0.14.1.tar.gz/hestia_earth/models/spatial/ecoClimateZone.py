from hestia_earth.schema import MeasurementStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import download, has_geospatial_data, _site_gadm_id
from . import MODEL

TERM_ID = 'ecoClimateZone'
BIBLIO_TITLE = 'Hiederer et al. 2010, Biofuels: A new methodology to estimate GHG emissions from global land use change'


def _measurement(value: int):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    measurement = _new_measurement(TERM_ID, MODEL, BIBLIO_TITLE)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _run(site: dict):
    reducer = 'mode'
    value = download(collection='users/hestiaplatform/climate_zone',
                     ee_type='raster',
                     reducer=reducer,
                     latitude=site.get('latitude'),
                     longitude=site.get('longitude'),
                     gadm_id=_site_gadm_id(site),
                     boundary=site.get('boundary'),
                     fields=reducer
                     ).get(reducer, None)

    return [] if value is None else [_measurement(round(value))]


def _should_run(site: dict):
    should_run = has_geospatial_data(site)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
