import os
from datetime import datetime
from zipfile import ZipFile

import pandas as pd
import wget

from midas.tools import LOG

BASE_URL = (
    "https://opendata.dwd.de/climate_environment/CDC/observations_germany/"
    "climate/hourly/"
)
# https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/historical/stundenwerte_TU_00691_19490101_20201231_hist.zip
AIR_URL = BASE_URL + (
    "air_temperature/historical/stundenwerte_TU_00691_19490101_20201231_hist"
    ".zip"
)
SOLAR_URL = BASE_URL + "solar/stundenwerte_ST_00691_row.zip"
WIND_URL = BASE_URL + (
    "wind/historical/stundenwerte_FF_00691_19260101_20201231_hist.zip"
)
SUN_URL = BASE_URL + (
    "sun/historical/stundenwerte_SD_00691_19510101_20201231_hist.zip"
)
CLOUD_URL = BASE_URL + (
    "cloudiness/historical/stundenwerte_N_00691_19490101_20201231_hist.zip"
)

# Horizontal solar radiation is provided as hourly sum in Joule/cm^2
# (i.e., correct would be Joule/s/cm^2 * 3600s), but we want Watt/m^2
# for our PV models. Since 1*W = 1*J/s we first need to get back to
# J/s by dividing by 3600. Next, we want to convert from cm^2 to m^2,
# which is by multiplying with 0.0001, however, since cm^2 is in the
# divisor, we need to divide by that value (or multiply with the
# reciprocal). So the calculation we need to apply is
# 1 / (3.6*1e^3) * 1 / 1e^-4 = 1e^4 / (3.6*1e^3) = 1e^1 / 3.6
# which is equal to:
JOULE_TO_WATT = 10 / 3.6
DATE_COL = 1
DATE_COL_SOL = 8
DATA_COLS = {
    "air": [("TT_TU", "t_air_degree_celsius", 1)],
    "solar": [
        ("FD_LBERG", "dh_w_per_m2", JOULE_TO_WATT),
        ("FG_LBERG", "gh_w_per_m2", JOULE_TO_WATT),
    ],
    "wind": [("   F", "wind_v_m_per_s", 1), ("   D", "wind_dir_degree", 1)],
    "cloud": [(" V_N", "cloud_percent", 12.5)],
    "sun": [("SD_SO", "sun_hours_min_per_h", 1)],
}


def build_weather_data(path, filename):
    if path is None:
        path = os.path.abspath(
            os.path.join(__file__, "..", "..", "..", "..", "data")
        )
    if filename is None:
        filename = "WeatherBre2009-2019.hdf5"
    output_path = os.path.abspath(os.path.join(path, filename))
    if os.path.exists(output_path):
        LOG.debug("Found existing datasets at %s.", output_path)
        return True

    LOG.debug("No dataset found. Start downloading weather data ...")
    tmp = os.path.join(path, "tmp")
    os.makedirs(tmp, exist_ok=True)

    air_fname = AIR_URL.rsplit("/", 1)[-1]
    if not os.path.exists(os.path.join(tmp, air_fname)):
        air_fname = wget.download(AIR_URL, out=tmp)

    sol_fname = SOLAR_URL.rsplit("/", 1)[-1]
    if not os.path.exists(os.path.join(tmp, sol_fname)):
        sol_fname = wget.download(SOLAR_URL, out=tmp)

    win_fname = WIND_URL.rsplit("/", 1)[-1]
    if not os.path.exists(os.path.join(tmp, win_fname)):
        win_fname = wget.download(WIND_URL, out=tmp)

    clo_fname = CLOUD_URL.rsplit("/", 1)[-1]
    if not os.path.exists(os.path.join(tmp, clo_fname)):
        clo_fname = wget.download(CLOUD_URL, out=tmp)

    sun_fname = SUN_URL.rsplit("/", 1)[-1]
    if not os.path.exists(os.path.join(tmp, sun_fname)):
        sun_fname = wget.download(SUN_URL, out=tmp)

    unzip(tmp, air_fname, "air")
    unzip(tmp, sol_fname, "solar")
    unzip(tmp, win_fname, "wind")
    unzip(tmp, clo_fname, "cloud")
    unzip(tmp, sun_fname, "sun")

    data = pd.DataFrame(
        index=pd.date_range(
            start="2009-01-01 00:00:00",
            end="2019-12-31 23:00:00",
            tz="Europe/Berlin",
            freq="H",
        )
    )
    data = load_data(tmp, "air", data)
    data = load_data(tmp, "solar", data)
    data = load_data(tmp, "wind", data)
    # data = load_data(tmp, "cloud", data)  # Length missmatch
    # data = load_data(tmp, "sun", data)

    # path = os.path.join(path, "weather_bre2009-2019.hdf5")
    data.to_hdf(output_path, "weather", "w")
    LOG.debug("Download complete.")


def unzip(path, fname, target):

    with ZipFile(os.path.join(path, fname), "r") as zip_ref:
        zip_ref.extractall(os.path.join(path, target))


def load_data(path, target, data):
    fname = os.path.join(path, target)
    files = os.listdir(fname)
    data_file = [f for f in files if f.startswith("produkt")][0]

    fname = os.path.join(fname, data_file)

    if target == "solar":
        parser = lambda date: datetime.strptime(date.split(":")[0], "%Y%m%d%H")
    else:
        parser = lambda date: datetime.strptime(date, "%Y%m%d%H")
    csv = pd.read_csv(
        fname, sep=";", index_col=1, parse_dates=[1], date_parser=parser
    )
    csv = csv.loc["2009-01-01 00:00:00":"2019-12-31 23:00:00"]
    for src_col, tar_col, fac in DATA_COLS[target]:

        data[tar_col] = csv[src_col].values * fac

        if target == "air":
            tar_col2 = f"day_avg_{tar_col}"
            data[tar_col2] = (
                csv[src_col].values.reshape(-1, 24).mean(axis=1).repeat(24)
            )

    return data
