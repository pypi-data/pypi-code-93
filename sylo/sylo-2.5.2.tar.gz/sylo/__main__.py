import logging
from sylo.args import get_arguments
from sylo.sylo import run
from sylo.sylo_logging import logging_config
from sylo.models import Config

logger = logging.getLogger(__name__)

config = Config()


def main():
    args = get_arguments()
    logging_config(args.log)
    run(args, config)
    logger.info("Started from __main__")


if __name__ == "__main__":

    main()
