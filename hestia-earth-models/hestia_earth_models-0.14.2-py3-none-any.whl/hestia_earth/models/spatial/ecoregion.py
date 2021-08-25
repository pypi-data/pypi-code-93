from hestia_earth.models.log import logger
from .utils import download, has_geospatial_data, _site_gadm_id
from . import MODEL


def _run(site: dict):
    # TODO Add a catch for points that fall outside of an ecoregion. Currently this will crash
    #  Replace with NA then use country in the biodiversity models
    field = 'eco_code'
    eco_code = download(collection='users/hestiaplatform/Terrestrial_Ecoregions_World',
                        ee_type='vector',
                        latitude=site.get('latitude'),
                        longitude=site.get('longitude'),
                        gadm_id=_site_gadm_id(site),
                        boundary=site.get('boundary'),
                        fields=field
                        ).get(field, None)

    logger.info('value=%s', eco_code)
    return eco_code


def _should_run(site: dict):
    should_run = has_geospatial_data(site)
    logger.info('model=%s, should_run=%s', MODEL, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else None
