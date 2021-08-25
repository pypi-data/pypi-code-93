from hestia_earth.schema import MeasurementStatsDefinition, TermTermType

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import download, has_geospatial_data, _site_gadm_id
from . import MODEL

TERM_ID = 'histosol'
BIBLIO_TITLE = 'The harmonized world soil database. verson 1.0'


def _measurement(value: float):
    logger.info('key=%s', TERM_ID)
    measurement = _new_measurement(TERM_ID, MODEL, BIBLIO_TITLE)
    measurement['value'] = [value]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _run(site: dict):
    reducer = 'mean'
    value = download(collection='users/hestiaplatform/histosols_perc',
                     ee_type='raster',
                     reducer=reducer,
                     latitude=site.get('latitude'),
                     longitude=site.get('longitude'),
                     gadm_id=_site_gadm_id(site),
                     boundary=site.get('boundary'),
                     fields=reducer
                     ).get(reducer, 0)

    return [_measurement(value)] if value > 0 else []


def _should_run(site: dict):
    measurements = site.get('measurements', [])
    has_soil_type = any([m for m in measurements if m.get('term', {}).get('termType') == TermTermType.SOILTYPE.value])
    should_run = has_geospatial_data(site) and not has_soil_type
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
