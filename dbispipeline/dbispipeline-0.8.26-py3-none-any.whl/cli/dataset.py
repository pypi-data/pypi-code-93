"""Tool to manage data."""
import os

from logzero import logger
import yaml

from dbispipeline import utils

LINK_CONFIG_FILE = 'data/links.yaml'


def link(dataset_dir=None):
    """Links the needed datasets to the dataset folder.

    The configuration is loaded from `data/links.yaml`.

    Args:
        dataset_dir: the prefix used for the dataset paths. Overrides
            default from dbispipeline. To use the pipeline config pass None.
    """
    if dataset_dir is None:
        project_config = utils.load_project_config()[utils.SECTION_PROJECT]
        dataset_dir = project_config[utils.OPTION_DATASET_DIR]

        if dataset_dir == '':
            logger.error('No dataset dir is defined. Look at the README.')
            exit(4)
    logger.info('Linking datasets from: %s' % dataset_dir)

    try:
        with open(LINK_CONFIG_FILE, 'r') as yml:
            try:
                config = yaml.safe_load(yml)
            except yaml.YAMLError as ex:
                logger.exception(ex)
    except FileNotFoundError:
        logger.error('No such file or directory: %s' % LINK_CONFIG_FILE)
        exit(1)

    try:
        for dataset in config['datasets']:
            _link_dataset(dataset_dir, dataset)
    except KeyError:
        logger.error('Config does not contain datasets.')
        exit(3)


def _link_dataset(dataset_dir, dataset):
    logger.info('\t- %s' % dataset)

    src = os.path.join(dataset_dir, dataset)
    if not os.path.isdir(src):
        logger.warn('Source is not directory: %s' % src)
        return

    dst = 'data'
    if not os.path.isdir(dst):
        logger.error('No destination data directory: %s' % dst)
        exit(2)

    dataset = os.path.join(*dataset.split('/')[1:])
    dst = os.path.join(dst, dataset)

    try:
        os.symlink(src, dst, target_is_directory=True)
    except FileExistsError:
        if not os.readlink(dst) == src:
            logger.warn('Wrong source: \'%s\' instead of \'%s\'' %
                        (os.readlink(dst), src))
