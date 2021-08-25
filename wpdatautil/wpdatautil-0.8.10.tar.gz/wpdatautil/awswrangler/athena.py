"""awswrangler athena utilities."""
import logging

import awswrangler as wr

from wpdatautil.object import fullname
from wpdatautil.timeit import Timer

log = logging.getLogger(__name__)


def run_query(sql: str, database: str, description: str = "query") -> None:
    """Run the given AWS Athena query, waiting until completion."""
    timer = Timer()
    log.info(f"Submitted the {description}.")
    try:
        wr.athena.wait_query(wr.athena.start_query_execution(sql=sql, database=database))
    except Exception as exception:
        log.error(f"Failed to complete the {description}: {fullname(exception)}: {exception}")
        raise
    log.info(f"Completed in {timer} the {description}.")
