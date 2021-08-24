import logging
from sylo.sylo import run
from sylo.args import get_arguments
from sylo.sylo_logging import logging_config
from sylo.models import Config

logger = logging.getLogger(__name__)

config = Config()


def main():
    args = get_arguments()
    logging_config(args.log)
    print(args.theme)
    run(args, config)
    logger.info("Started from cli")
