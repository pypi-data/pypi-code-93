import importlib.util
import logging
import os
from argparse import Namespace

from sp_devtools.context import LocalStorage


def run_scraper(namespace: Namespace) -> None:
    logging.info('Executing the script...')
    LocalStorage.STORAGE_PATH = namespace.output
    spec = importlib.util.spec_from_file_location("script", namespace.input)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    try:
        script.custom_scraper_script(**namespace.params)
        logging.info(f'Finished execution. Results count: {len(set(script.context.series_ids))}')
    except Exception as e:
        logging.error('Exception during scraper run:', exc_info=True)
