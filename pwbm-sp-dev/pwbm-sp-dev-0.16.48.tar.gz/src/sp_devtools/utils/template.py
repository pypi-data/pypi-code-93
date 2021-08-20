import logging
import shutil
from argparse import Namespace
from pathlib import Path


def create_template(namespace: Namespace) -> None:
    source_path = Path(__file__).parent.parent / 'templates' / 'base.py'
    dest_path = namespace.output.absolute()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_path, dest_path)
    logging.info(f'Boilerplate script created: {dest_path}')
