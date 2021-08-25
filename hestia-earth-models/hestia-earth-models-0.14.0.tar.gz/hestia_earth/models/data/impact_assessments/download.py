import os
import glob
import json
from concurrent.futures import ThreadPoolExecutor
from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia, find_node

from hestia_earth.models.log import logger
from .utils import get_dir

SOURCE_NAME = 'Wernet et al (2016)'
EXT = '.jsonld'


def get_files(): return list(filter(lambda f: f.endswith(EXT), os.listdir(get_dir())))


def _save_assessment(id: str):
    data = download_hestia(id, SchemaType.IMPACTASSESSMENT)
    file_path = f"{get_dir()}/{id}.jsonld"
    logger.debug(f"saving {file_path}...")
    with open(file_path, 'w') as f:
        return json.dump(data, f, indent=2)


def _run():
    logger.info('Downloading Impacts...')

    nodes = find_node(SchemaType.IMPACTASSESSMENT, {'source.name.keyword': SOURCE_NAME}, 1000)
    nodes = [node.get('@id') for node in nodes]
    logger.debug('Found %s matching impacts', len(nodes))

    with ThreadPoolExecutor() as executor:
        executor.map(_save_assessment, nodes)

    logger.info('Impacts downloaded.')


def _file_exists(filename: str):
    exists = False
    try:
        id = filename.replace(EXT, '')
        data = download_hestia(id, SchemaType.IMPACTASSESSMENT)
        exists = '@id' in data
    except Exception:
        exists = False
    # read the first file to make sure the impact still exists, if not remove all and force re-download
    if not exists:
        files = glob.iglob(os.path.join(get_dir(), '*' + EXT))
        for filepath in files:
            os.remove(filepath)
    return exists


def _should_run():
    files = get_files()
    should_run = len(files) == 0 or not _file_exists(files[0])
    logger.debug('Should download impacts: %s', should_run)
    return should_run


def run(): return _run() if _should_run() else None
