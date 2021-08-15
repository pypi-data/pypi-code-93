import configparser
import datetime
import os

config = configparser.ConfigParser()

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
config.read(config_path)

LAST_UPDATED_ON = datetime.datetime.now().strftime("%Y-%m-%d")
FMT_DATE_TIME = config.get("datetime_format", "FMT_DATE_TIME")
FMT_TIME = config.get("datetime_format", "FMT_TIME")
FMT_DATE_CONSTANT_TIME = config.get("datetime_format", "FMT_DATE_CONSTANT_TIME")
FMT_68 = config.get("datetime_format", "FMT_68")
START_TIME = config.get("datetime_format", "START_TIME")
END_TIME = config.get("datetime_format", "END_TIME")
LAST_HOUR = config.get("datetime_format", "LAST_HOUR")

TICKERS_FILE = config.get("data_path", "TICKERS_FILE")
SECTOR_CODES_PATH = config.get("data_path", "SECTOR_CODES_PATH")
SECTOR_TICKERS_PATH = config.get("data_path", "SECTOR_TICKERS_PATH")
GROUP_TICKERS_PATH = config.get("data_path", "GROUP_TICKERS_PATH")
DATASTORE_PATH = config.get("data_path", "DATASTORE_PATH")
DATASTORE_COPHIEU68_PATH = config.get("data_path", "DATASTORE_COPHIEU68_PATH")
DATASTORE_VND_PATH = config.get("data_path", "DATASTORE_VND_PATH")
