from hestia_earth.models.log import logger
from .utils import download, has_geospatial_data, _site_gadm_id
from . import MODEL


def _run(site: dict):
    field = 'Name'
    awareId = download(collection='users/hestiaplatform/AWARE',
                       ee_type='vector',
                       latitude=site.get('latitude'),
                       longitude=site.get('longitude'),
                       gadm_id=_site_gadm_id(site),
                       boundary=site.get('boundary'),
                       fields=field
                       ).get(field, None)

    logger.info('value=%s', awareId)
    return awareId


def _should_run(site: dict):
    should_run = has_geospatial_data(site)
    logger.info('model=%s, should_run=%s', MODEL, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else None
