import logging
import sys


def init_logging(stream=sys.stderr, level=logging.DEBUG):
    stderr_handler = logging.StreamHandler(stream)
    stderr_handler.setFormatter(
        logging.Formatter(
            fmt='%(asctime)s.%(msecs)03d [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        ),
    )
    logging.basicConfig(
        level=level,
        handlers=[
            stderr_handler,
        ],
    )
