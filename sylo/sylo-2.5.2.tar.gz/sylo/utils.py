import os
import logging
import subprocess
import sys
from typing import List
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


def get_input(text):
    return input(text)


def valid_input(text, allowed_list: List):
    logger.info(f"Validating user choice against list: {allowed_list}")
    allowed_list_strings = [str(al) for al in allowed_list]
    if text.lower() in allowed_list_strings:
        return True
    else:
        return False


def run_subprocess(script: str):
    if "rm " in script:
        logger.warning("UNSAFE SCRIPT")
        sys.exit()
    try:
        subprocess.run(script, shell=True, check=True, timeout=30)
    except subprocess.CalledProcessError:
        print(
            "Insights panel not loading as there is no data to display. "
            "\nTry working for a few mins then check back later."
        )
        print("\n")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def mins_to_secs(minutes: int):
    return minutes * 60


def flip_mode(mode: str):
    if mode == "work":
        logger.debug(f"flip_mode took {mode} returned rest")
        return "rest"
    else:
        logger.debug(f"flip_mode took {mode} returned work")
        return "work"


def check_for_file(path):
    is_file = os.path.isfile(path)
    logger.info(f"check_for_file {path} {is_file}")
    return is_file


def check_for_dir(path):
    is_dir = os.path.isdir(path)
    logger.info(f"check_for_file {path} {is_dir}")
    return is_dir


def get_today():
    return datetime.now().date().strftime("%Y-%m-%d")


def get_weekday():
    return datetime.now().weekday()


def read_from_file(path):
    with open(path, "r") as read_file:
        return read_file.read()


def generate_date_range(end_date: str, number_of_days: int):
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)
    date_list = []
    for day in range(number_of_days):
        date_list.append(datetime.strftime(end_date_dt, "%Y-%m-%d"))
        end_date_dt -= delta
    date_list.sort()
    return date_list


def strike(text):
    return "".join(["\u0336{}".format(c) for c in text])
