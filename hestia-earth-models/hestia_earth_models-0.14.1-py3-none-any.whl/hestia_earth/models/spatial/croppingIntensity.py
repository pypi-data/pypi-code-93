from hestia_earth.schema import PracticeStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.measurement import _new_measurement
from hestia_earth.models.utils.site import valid_site_type
from .utils import download, has_geospatial_data, _site_gadm_id
from . import MODEL

TERM_ID = 'croppingIntensity'


def _measurement(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement['value'] = [value]
    measurement['statsDefinition'] = PracticeStatsDefinition.SPATIAL.value
    return measurement


def _run(site: dict):
    reducer = 'sum'

    # 1) extract maximum monthly growing area (MMGA)
    MMGA_value = download(collection='users/hestiaplatform/MMGA',
                          ee_type='raster',
                          reducer=reducer,
                          latitude=site.get('latitude'),
                          longitude=site.get('longitude'),
                          gadm_id=_site_gadm_id(site),
                          boundary=site.get('boundary'),
                          fields=reducer
                          )
    MMGA_value = MMGA_value.get('first', MMGA_value.get('sum', 0))

    # 2) extract area harvested (AH)
    AH_value = download(collection='users/hestiaplatform/AH',
                        ee_type='raster',
                        reducer=reducer,
                        latitude=site.get('latitude'),
                        longitude=site.get('longitude'),
                        gadm_id=_site_gadm_id(site),
                        boundary=site.get('boundary'),
                        fields=reducer
                        )
    AH_value = AH_value.get('first', AH_value.get('sum'))

    # 3) estimate croppingIntensity from MMGA and AH.
    value = None if MMGA_value is None or AH_value is None or AH_value == 0 else (MMGA_value / AH_value)

    return [] if value is None else [_measurement(value)]


def _should_run(site: dict):
    should_run = has_geospatial_data(site) and valid_site_type(site)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
