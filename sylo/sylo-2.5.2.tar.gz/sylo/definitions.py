import os
import datetime
from pathlib import Path


HOME_DIR = home = str(Path.home())
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE_LOCATION = f"{HOME_DIR}/.sylo/sylo.cfg"
HOME_DIR_CREATE = f"mkdir {HOME_DIR}/.sylo"
SYLO_HOME = f"{HOME_DIR}/.sylo"


INPUT_OPTIONS = {
    "home": ["", "h", "q", "s", "t", "y", "i", "a"],
    "task_menu": ["", "c", "m", "n", "d", "l"],
}


TIMER_DEFAULTS = {
    "work": {
        "mins": 25,
        "secs": 1500,
    },
    "rest": {
        "mins": 5,
        "secs": 300,
    },
}

COUNTDOWN_INCREMENTS = 1

METRICS_HEAT = 'termgraph --calendar --color magenta --start-dt "%s" %s 2>/dev/null'

METRICS_BAR = 'termgraph %s --color {red,green} --start-dt "%s" 2>/dev/null'

SQLITE_DB = f"{HOME_DIR}/.sylo/_sylo.db"

BOOTSTRAP_SQL = f"{ROOT_DIR}/database_interactions/bootstrap.sql"

INSIGHTS_FILE_SESSIONS = f"{HOME_DIR}/.sylo/insights_sessions.dat"
INSIGHTS_FILE_POMS = f"{HOME_DIR}/.sylo/insights_poms.dat"
FORTNIGHT_AGO = (datetime.datetime.now() - datetime.timedelta(days=14)).date()
ONE_YEAR_AGO = (datetime.datetime.now() - datetime.timedelta(days=364)).date()
