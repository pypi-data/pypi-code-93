"""Main module to run the Twitter collector and set up the database.
When run as main it requires two arguments, `-rc` for the time the 
collector should be run in 24hour time, and `-o` for the name (and location if needed)
of the output database file.
The collector will then run daily at that time."""

import logging
from schedule import Scheduler
import datetime
import time
import traceback
from traceback import format_exc
from argparse import ArgumentParser

from .utils.database import Database
from .utils.search import FullArchiveSearch
from .utils.geolocation import MatchPlaces

# Set up logging
logging.basicConfig(
    filename="twitter.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Initialise logger
logger = logging.getLogger(__name__)

# Source https://gist.github.com/mplewis/8483f1c24f2d6259aef6
class SafeScheduler(Scheduler):
    """
    An implementation of Scheduler that catches jobs that fail, logs their
    exception tracebacks as errors, optionally reschedules the jobs for their
    next run time, and keeps going.

    Use this to run jobs that may or may not crash without worrying about
    whether other jobs will run or if they'll crash the entire script.
    """

    def __init__(self, reschedule_on_failure=True):
        """
        If reschedule_on_failure is True, jobs will be rescheduled for their
        next run as if they had completed successfully. If False, they'll run
        on the next run_pending() tick.
        """
        self.reschedule_on_failure = reschedule_on_failure
        super().__init__()

    def _run_job(self, job):
        try:
            super()._run_job(job)
        except Exception:
            logger.error(format_exc())
            job.last_run = datetime.datetime.now()
            job._schedule_next_run()


# Now set the twitter collection function to run every day
logger.info("Starting scheduler...")

# Database(DB).get_unmatched_tweets()
def daily_job(db_location):
    # Set up the database object
    db = Database(db_location)
    # Run the full archive search to update the tweets to midnight yesterday
    FullArchiveSearch(db).get_tweets()
    # Now, get the matched places, passing in the db of places currently unmatched
    matched = MatchPlaces(db.get_unmatched_places()).get()
    # Write these results to the database
    db.write_matched_places(matched)


def start_tweets_collection(args):
    # Define a SafeScheduler object
    scheduler = SafeScheduler()
    try:
        scheduler.every().day.at(args.collector_time).do(daily_job, args.db_location)

        logger.info(
            "Sheduler set to run every day at {}, with the database at {}".format(
                args.collector_time, args.db_location
            )
        )

        # Sleep function
        while True:
            scheduler.run_pending()
            time.sleep(60)

    except KeyboardInterrupt:
        logger.warn("Scheduler stopped with keyboard interrupt.")

    except Exception:
        logger.critical(
            "Running script terminated. Traceback was {}".format(traceback.format_exc())
        )


if __name__ == "__main__":
    # Define some arguments
    parser = ArgumentParser()
    parser.add_argument(
        "-ct", "--run-collecter-at", dest="collector_time", type=str, default="09:00"
    )
    parser.add_argument(
        "-o", "--db-location", type=str, default="phw_tweets.db", dest="db_location"
    )
    args = parser.parse_args()
    start_tweets_collection(args)