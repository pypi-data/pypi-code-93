""" This is a full integration test.

The runtime for this script is several hours as it loops over all
eco-regions and check if we receive data for that. As such, it tests
all API calls and functionalities.

This also tests the functionality with the protected IUCN data (GISD and
Red-List).
The IUCN redlist file needs to be specified at the beginnin of the script.
For the GISD file, the automatic gisd downloader and parser will be used - the
location for storing the data must be specified also at the beginning of the
file.
See the documentation at https://marinvaders.gitlab.io/marinvaders/iucn_data/


"""
import sys
import logging
import logging.handlers
from pathlib import Path
import os


# path of the existing redlist data file
REDLIST_FILE = "/home/konstans/tmp/redlist/assessments.csv"

# location to store the automatically downloaded gisd data
GISD_FILE = "/home/konstans/tmp/gisd_data.json"


TESTPATH = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(TESTPATH, ".."))

import marinvaders  # noqa
import marinvaders.util  # noqa

if __name__ == "__main__":
    # Logging to console and file, with each run in a different file
    logpath = TESTPATH / "evaluation_logs"
    logpath.mkdir(exist_ok=True, parents=True)
    logfile = logpath / "integration_evaluation.log"
    ig_log = logging.getLogger(__name__)
    ig_log.setLevel(logging.INFO)

    _do_rollover = True if os.path.exists(logfile) else False
    loghandler_file = logging.handlers.RotatingFileHandler(
        filename=logfile, backupCount=50
    )
    if _do_rollover:
        loghandler_file.doRollover()

    loghandler_stream = logging.StreamHandler()
    log_format = logging.Formatter(
        fmt="%(asctime)s %(levelname)-4s %(filename)s - %(funcName)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    loghandler_file.setFormatter(log_format)
    loghandler_stream.setFormatter(log_format)
    ig_log.addHandler(loghandler_file)
    ig_log.addHandler(loghandler_stream)

    ig_log.info("Start logging to {} and screen".format(logfile))
    exceptions = []

    ig_log.info("Start downloading GISD data to {GISD_FILE}")
    try:
        marinvaders.util.get_gisd(GISD_FILE)
    except Exception as e:
        ig_log.exception(f"{e}")
        exceptions.append(e)

    # Testing the species class with GISD data

    red_lionfish_aphia = 159559
    try:
        ig_log.info(f"Testing species class for {red_lionfish_aphia}")
        lionfish = marinvaders.Species(aphia_id=red_lionfish_aphia, gisd_file=GISD_FILE)
        gisd_reports = lionfish.reported_as_alien[
            lionfish.reported_as_alien["dataset"].str.contains("GISD")
        ]
        worms_reports = lionfish.reported_as_alien[
            lionfish.reported_as_alien["dataset"].str.contains("WoRMS")
        ]
        natcon_reports = lionfish.reported_as_alien[
            lionfish.reported_as_alien["dataset"].str.contains("NatCon")
        ]
        ig_log.info(f"WoRMS alien reports: {len(worms_reports)}")
        ig_log.info(f"GISD alien reports: {len(gisd_reports)}")
        ig_log.info(f"NatCon alien reports: {len(natcon_reports)}")
        if len(worms_reports) == 0:
            raise ValueError(f"WoRMS fails to report alien for {red_lionfish_aphia}")
        if len(gisd_reports) == 0:
            raise ValueError(f"GIDS fails to report alien for {red_lionfish_aphia}")
        if len(natcon_reports) == 0:
            raise ValueError(f"NatCon fails to report alien for {red_lionfish_aphia}")

    except Exception as e:
        ig_log.exception(f"Exception for aphia id {red_lionfish_aphia}: {e}")
        exceptions.append(e)

    # Testing all marine ecoregions
    df_er = marinvaders.marine_ecoregions()

    for run_nr, run_data in df_er.iterrows():
        try:
            ig_log.info(f"LOOP {run_nr}: {run_data.ECOREGION} - {run_data.ECO_CODE}")
            reg_data = marinvaders.MarineLife(
                eco_code=run_data.ECO_CODE,
                gisd_file=GISD_FILE,
                redlist_file=REDLIST_FILE,
            )
            ig_log.info(f"Received species - total: {len(reg_data.all_species)}")
            ig_log.info(f"Received species - alien: {len(reg_data.alien_species)}")
            ig_log.info(
                f"Received species - affected: {len(reg_data.affected_by_invasive)}"
            )
        except Exception as e:
            ig_log.exception(f"Exception for eco-code {run_data.ECO_CODE}:")
            exceptions.append(e)

    ig_log.info("Finished integration test run")
    if len(exceptions) == 0:
        ig_log.info("All tests run as expected")
    else:
        ig_log.exception("EXCEPTIONS:")
        for exep in exceptions:
            ig_log.exception(exep)
        ig_log.exception("EXCEPTIONS OCCURED - these are also logged further up")

    # removing the logging handlers for next interactive run
    ig_log.handlers = []
