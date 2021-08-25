from biolib.biolib_logging import logger
from biolib.compute_node.job_worker.executors.types import SendSystemExceptionType


class ComputeProcessException(Exception):
    def __init__(self, original_error: Exception, biolib_error_code, send_system_exception: SendSystemExceptionType):
        super().__init__()

        send_system_exception(biolib_error_code)
        logger.error(original_error)
