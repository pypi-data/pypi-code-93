from .get_logging_config import get_logging_config
from .logged_route import *


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return False


# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
