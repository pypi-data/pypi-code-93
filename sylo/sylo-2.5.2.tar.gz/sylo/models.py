import logging
from dataclasses import dataclass
from sylo.definitions import (
    TIMER_DEFAULTS,
    CONFIG_FILE_LOCATION,
    SQLITE_DB,
)
from sylo.utils import check_for_file, mins_to_secs, get_today
import tomli
import sqlite3


logger = logging.getLogger(__name__)


@dataclass
class Rest:
    mins: int = TIMER_DEFAULTS["rest"]["mins"]
    secs: int = TIMER_DEFAULTS["rest"]["secs"]
    bar_color: str = "green"


@dataclass
class Work:
    mins: int = TIMER_DEFAULTS["work"]["mins"]
    secs: int = TIMER_DEFAULTS["work"]["secs"]
    bar_color: str = "red"


@dataclass
class Durations:
    work = Work
    rest = Rest
    total_work_mins: float = 0
    total_rest_mins: float = 0
    poms = float = 0

    def __post_init__(self):
        self.work = Work()
        self.rest = Rest()


@dataclass
class Config:
    theme_color = "rainbow"
    fewer_colors = 0
    audio_file = None
    work_time = 25
    rest_time = 5
    pom_name = "Pomodoro"


class ConfigFile:
    def __init__(self):
        self.config_file = CONFIG_FILE_LOCATION
        self.is_config = check_for_file(self.config_file)

    def load_config(self):
        with open(self.config_file, encoding="utf-8") as f:
            return tomli.load(f)

    def set_config(self, config: Config, durations_model: Durations):
        if self.is_config is True:
            config_file = self.load_config()
            logger.info(config_file)
            try:
                general = config_file["general"]
                config.audio_file = general["audio_file"]
                logger.info(f"CONFIG:set audio_file to {config.audio_file}")
            except KeyError as k:
                logger.info(k)
                pass
            try:
                general = config_file["general"]
                config.pom_name = general["time_segment_name"]
                logger.info(f"CONFIG:set pom_name to {config.pom_name}")
            except KeyError as k:
                logger.info(k)
                pass
            try:
                durations = config_file["durations"]
                logger.info(f"CONFIG: durations from file: {durations}")
                durations_model.work.mins = durations["work"]
                durations_model.work.secs = mins_to_secs(durations["work"])
                durations_model.rest.mins = durations["rest"]
                durations_model.rest.secs = mins_to_secs(durations["rest"])
            except KeyError as k:
                logger.info(k)
                pass
            try:
                general = config_file["display"]
                logger.info(f"CONFIG: general from file: {general}")
                config.theme_color = general["theme"]
                logger.info(f"CONFIG:set theme_color to {config.theme_color}")
            except KeyError as k:
                logger.info(k)
                pass
            try:
                general = config_file["display"]
                config.fewer_colors = general["fewer_colors"]
                logger.info(f"CONFIG:set simple_colors to {config.fewer_colors}")
            except KeyError as k:
                logger.info(k)
                pass


class Database:
    def __init__(self):
        self.db_file = SQLITE_DB

    def _connect(self):
        return sqlite3.connect(self.db_file)

    def execute(self, query: str):
        con = self._connect()
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()

    def execute_script(self, query: str):
        con = self._connect()
        cur = con.cursor()
        cur.executescript(query)
        con.commit()
        con.close()

    def select(self, query: str):
        con = self._connect()
        cur = con.cursor()
        result = cur.execute(query)
        data = result.fetchall()
        cur.close()
        return data

    def execute_from_file(self, file: str):
        with open(file, "r") as read_file:
            query = read_file.read()
        self.execute_script(query)

    def select_from_file(self, file: str):
        with open(file, "r") as read_file:
            query = read_file.read()
        return self.select(query)

    def bootstrap_on_first_boot(self):
        self.execute_script(bootstrap())

    def initial_data_load(self, durations: Durations):
        (session_data,) = (
            self.select(
                f"SELECT * FROM sessions where session_date = '{get_today()}';"
            ),
        )
        (poms_data,) = (
            self.select(f"SELECT * FROM poms where poms_date = '{get_today()}';"),
        )
        try:
            logger.info(session_data)
            work_time_today = session_data[0][1]
            rest_time_today = session_data[0][2]
            logger.info(f"Work time loaded on boot: {work_time_today}")
            logger.info(f"Rest time loaded on boot: {rest_time_today}")
            durations.total_work_mins = work_time_today
            durations.total_rest_mins = rest_time_today
            logger.info("data_load_on_boot Found data for today")
        except Exception as e:
            logger.info(e)
            logger.info("data_load_on_boot NO DATA for today")
        if session_data is None:
            durations.total_rest_mins = 0
            durations.total_work_mins = 0

        try:
            logger.info(poms_data)
            poms_today = poms_data[0][1]
            logger.info(f"Poms loaded on boot: {poms_today}")
            durations.poms = poms_today
            logger.info("data_load_on_boot Found poms for today")
        except Exception as e:
            logger.info(e)
            logger.info("data_load_on_boot NO DATA for today")
        if poms_data is None:
            durations.poms = 0


def bootstrap():
    return """
    CREATE TABLE IF NOT EXISTS sessions (
        session_date date,
        time_worked REAL,
        time_rested REAL,
        UNIQUE(session_date)
    );

    CREATE TABLE IF NOT EXISTS poms (
        poms_date date,
        poms int,
        UNIQUE(poms_date)
        );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        created_at date,
        completed_at date,
        assigned_date date,
        description text,
        effort int,
        complete bool,
        number_of_times_moved int
    );
    """
