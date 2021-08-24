"""This module contains functions to load and create MIDAS
configuration files.

"""
import os
from pathlib import Path
import shutil
import click
from configparser import ConfigParser

from midas.tools import LOG
from .commercial_data import build_commercial_data
from .default_load_profiles_data import build_dlp_data
from .simbench_data import build_simbench_data
from .smartnord_data import build_smartnord_data
from .weather_data import build_weather_data


MIDAS_CFG_FILE = "midas.ini"
MIDAS_CFG_FOLDER = ".midas"
MIDAS_DATA_FOLDER = "midas_data"
MIDAS_CFG_PATHS = [
    os.path.join(os.getcwd()),
    os.path.join(str(Path.home()), MIDAS_CFG_FOLDER),
]


def check_config(path=None):
    cfgparse = ConfigParser()

    if path is None:
        for path in MIDAS_CFG_PATHS:
            cfg_path = os.path.join(path, MIDAS_CFG_FILE)
            if os.path.isfile(cfg_path):
                cfgparse.read(cfg_path)
                return cfgparse

    else:
        cfgparse.read(path)
        return cfgparse

    LOG.info("No configuration found.")
    # At this point, a config is either found or needs to be created
    return None


def dialog(ini_path=None, data_path=None, autocfg=False):
    if autocfg:
        ini_path = MIDAS_CFG_PATHS[1]
        return create_config(ini_path, False, None)

    if ini_path is None:
        # TODO: Be more precise
        click.echo(
            "#############\n# MIDAS CLI #\n#############\n"
            "It seems you're using MIDAS for the first time. We need to perform a short\n"
            "setup. MIDAS will create a folder in your home directory where a\n"
            "configuration file will be created. Alternatively, the configuration file can\n"
            "be created in the current directory (but changing the current directory will\n"
            "pop up this dialog again)."
        )
        rsp = click.prompt(
            "# STEP 1 #\n"
            "Do you want to create a midas folder in your home directory to store the\n"
            "configuration file (y|n)?",
            default="y",
        )
        if rsp.lower() in ["y", "j", "yes", "ja"]:
            ini_path = MIDAS_CFG_PATHS[1]
        else:
            ini_path = MIDAS_CFG_PATHS[0]

    if data_path is None:

        rsp = click.prompt(
            "# STEP 2 #\n"
            "MIDAS will download the data sets required by certain simulators. Please\n"
            "provide a path, were the datasets should be stored. Type 'no' if you don't\n"
            "want to download the datasets (You need to specifiy the data path manually in\n"
            "the newly created midas.ini). Type '.' to use the current directy or specify\n"
            "any other path you like. If you press enter without typing, the default \n"
            "location will be used (|no|.|<any path you like>):",
            default="",
        )
        skip_data = False
        if len(rsp) > 0:
            if rsp == "no":
                skip_data = True
            elif rsp == ".":
                data_path = os.path.abspath(os.path.join(os.getcwd()))
            else:
                try:
                    data_path = os.path.abspath(os.path.join(rsp))
                except OSError as err:
                    click.echo(
                        "Something went wrong with your path. Please restart the program"
                    )
                    return False
        else:
            data_path = None

    return create_config(ini_path, skip_data, data_path)


def create_config(ini_path=False, skip_data=False, data_path=None):
    cfgparse = ConfigParser()

    cfg_path = os.path.join(ini_path, MIDAS_CFG_FILE)
    if data_path is None:
        data_path = os.path.join(ini_path, MIDAS_DATA_FOLDER)

    if not skip_data:
        os.makedirs(data_path, exist_ok=True)

    cfgparse["PATHS"] = {"data_path": data_path, "output_prefix": "_outputs"}
    cfgparse["DATA"] = {
        "commercial_name": "CommercialsRefTMY3.hdf5",
        "default_load_profiles_name": "DefaultLoadProfiles.hdf5",
        "simbench_name": "1-LV-rural3--0-sw.hdf5",
        "smart_nord_name": "SmartNordProfiles.hdf5",
        "weather_name": "WeatherBre2009-2019.hdf5",
        "load_commercial": True,
        "load_default_load_profiles": True,
        "load_simbench": True,
        "load_smart_nord": True,
        "load_weather": True,
    }
    cfgparse["MISC"] = {"seed_max": 1_000_000}

    with open(cfg_path, "w") as cfgfile:
        cfgparse.write(cfgfile)

    return True


def check_data(cfg):
    data_path = cfg["PATHS"]["data_path"]
    os.makedirs(data_path, exist_ok=True)
    LOG.debug("Checking datasets ...")

    # if cfg["DATA"]["load_commercial"].lower() == "true":
    #     build_commercial_data(
    #         path=data_path, filename=cfg["DATA"]["commercial_name"]
    #     )

    if cfg["DATA"]["load_default_load_profiles"].lower() == "true":
        build_dlp_data(
            path=data_path, filename=cfg["DATA"]["default_load_profiles_name"]
        )

    if cfg["DATA"]["load_simbench"].lower() == "true":
        build_simbench_data(
            path=data_path, simbench_code=cfg["DATA"]["simbench_name"][:-5]
        )

    if cfg["DATA"]["load_smart_nord"].lower() == "true":
        build_smartnord_data(
            path=data_path, filename=cfg["DATA"]["smart_nord_name"]
        )

    if cfg["DATA"]["load_weather"].lower() == "true":
        build_weather_data(
            path=data_path, filename=cfg["DATA"]["weather_name"]
        )

    try:
        shutil.rmtree(os.path.join(data_path, "tmp"))
    except OSError as e:
        pass

    LOG.debug("Checking datasets complete.")
    return True


if __name__ == "__main__":
    check_config()
