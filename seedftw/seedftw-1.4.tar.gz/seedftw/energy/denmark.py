"""
Functions related to data loading in Denmark.

"""

import urllib.parse
from datetime import datetime, timedelta

# For caching
from functools import lru_cache

# Import all useful libraries
import pandas as pd
from seedftw.base.timeseries import format_to_timetable, now


# Loading data from Energinet
@lru_cache(maxsize=10)
def __dk_energinet_dataservice_call(sql_query, output_format="Dataframe"):

    # Determine the URL to use for the call
    url = (
        "https://www.energidataservice.dk/proxy/api/datastore_search_sql?sql="
        + urllib.parse.quote(sql_query)
    )

    # Read data in Json format
    api_data = pd.read_json(url)

    if any(api_data.success) == False:
        print("Failure in the API call")

    if output_format == "Dataframe":
        api_data = pd.DataFrame.from_records(api_data["result"].records)

    return api_data


def __format_time(t_in):
    if isinstance(t_in, datetime):
        t = t_in
    elif isinstance(t_in, str):
        t = pd.to_datetime(t_in)
    else:
        raise Exception("Illegal type for time (only supporting string and datetime")
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def __format_start_end(start, end):
    start = __format_time(start)
    end = __format_time(end)
    return start, end


def __format_data_table_co2_per_area(data):
    column_dict = {
        "CO2Emission": "co2_intensity",
        "PriceArea": "price_area",
    }
    return format_to_timetable(
        data, time_column="Minutes5UTC", column_dict=column_dict, utc_index=True
    )


def __format_data_table_co2_per_distribution(data):
    column_dict = {
        "Co2PerkWh": "co2_intensity",
        "PriceArea": "price_area",
        "Co2PerkWh_200": "co2_intensity_200pc",
    }
    return format_to_timetable(
        data, time_column="HourUTC", column_dict=column_dict, utc_index=True
    )


def electricity_average_co2_intensity(
    area="",
    start=None,
    end=None,
):
    if start is None:
        start = now() - timedelta(hours=168)
    if end is None:
        end = now()

    start, end = __format_start_end(start, end)

    if area == "DK1":
        condition2use = """WHERE "PriceArea" = 'DK1' AND"""

    elif area == "DK2":
        condition2use = """WHERE "PriceArea" = 'DK2' AND"""

    else:
        condition2use = """WHERE"""

    query2use = f"""SELECT "Minutes5UTC", "PriceArea", "CO2Emission" FROM "co2emis" {condition2use} "Minutes5UTC" >= '{start}' AND "Minutes5UTC" <= '{end}' ORDER BY "Minutes5UTC" ASC"""

    co2_data = __dk_energinet_dataservice_call(
        sql_query=query2use, output_format="Dataframe"
    )
    return __format_data_table_co2_per_area(co2_data)


def electricity_average_co2_intensity_forecast(
    area="",
    start=None,
    end=None,
):

    if start is None:
        start = now()
    if end is None:
        end = now() + timedelta(hours=24)
    start, end = __format_start_end(start, end)

    if area == "DK1":
        condition2use = """WHERE "PriceArea" = 'DK1' AND"""

    elif area == "DK2":
        condition2use = """WHERE "PriceArea" = 'DK2' AND"""

    else:
        condition2use = """WHERE"""

    query2use = f"""SELECT "Minutes5UTC", "PriceArea", "CO2Emission" FROM "co2emisprog" {condition2use} "Minutes5UTC" >= '{start}' AND "Minutes5UTC" <= '{end}' ORDER BY "Minutes5UTC" ASC"""

    co2_data = __dk_energinet_dataservice_call(
        sql_query=query2use, output_format="Dataframe"
    )
    return __format_data_table_co2_per_area(co2_data)


def electricity_distribution_average_co2_intensity(
    start=None,
    end=None,
):
    if start is None:
        start = now() - timedelta(days=365)
    if end is None:
        end = now()

    start, end = __format_start_end(start, end)

    query2use = f"""SELECT "HourUTC", "Co2PerkWh", "Co2PerkWh_200", "PriceArea" FROM "declarationemissionhour" WHERE "HourUTC">='{start}' AND "HourUTC"<='{end}' ORDER BY "HourUTC" ASC"""

    co2_data = __dk_energinet_dataservice_call(
        sql_query=query2use, output_format="Dataframe"
    )
    return __format_data_table_co2_per_distribution(co2_data)


def electricity_balance(
    area="",
    start=None,
    end=None,
):
    # Doc available here: https://www.energidataservice.dk/tso-electricity/electricitybalance
    if start is None:
        start = now() - timedelta(days=15)
    if end is None:
        end = now()

    start, end = __format_start_end(start, end)

    if area == "DK1":
        condition2use = """ "PriceArea" = 'DK1' AND"""

    elif area == "DK2":
        condition2use = """ "PriceArea" = 'DK2' AND"""

    else:
        condition2use = ""

    query2use = (
        """SELECT "HourUTC", "GrossCon", "ElectricBoilerCon", "NetCon","""
        + """ "LocalPowerProd", "ExchangeGreatBelt","OffshoreWindPower","""
        + """ "CentralProd","ExchangeNordicCountries",	"ExchangeContinent","""
        + """ "PriceArea",	"OnshoreWindPower",	"SolarPowerProd" """
        + """FROM "electricitybalance" """
        + f"""WHERE{condition2use} "HourUTC">='{start}' AND "HourUTC"<='{end}' """
        + ' ORDER BY "HourUTC" ASC'
    )

    dict2use = {
        "GrossCon": "gross_demand",
        "ElectricBoilerCon": "electric_boiler_demand",
        "NetCon": "net_demand",
        "LocalPowerProd": "local_power_generation",
        "ExchangeGreatBelt": "exchange_great_belt",
        "OffshoreWindPower": "offshore_wind_generation",
        "CentralProd": "central_generation",
        "ExchangeNordicCountries": "exchange_nordics",
        "ExchangeContinent": "exchange_continent",
        "OnshoreWindPower": "onshore_wind_generation",
        "SolarPowerProd": "solar_generation",
        "PriceArea": "price_area",
    }

    data = __dk_energinet_dataservice_call(
        sql_query=query2use, output_format="Dataframe"
    )
    return format_to_timetable(
        data, time_column="HourUTC", column_dict=dict2use, utc_index=True
    )


def electricity_production_and_exchange(
    area="",
    start=None,
    end=None,
):
    # Doc available here: https://www.energidataservice.dk/tso-electricity/electricityprodex5minrealtime
    if start is None:
        start = now() - timedelta(days=2)
    if end is None:
        end = now()

    start, end = __format_start_end(start, end)

    if area == "DK1":
        condition2use = """ "PriceArea" = 'DK1' AND"""

    elif area == "DK2":
        condition2use = """ "PriceArea" = 'DK2' AND"""

    else:
        condition2use = ""

    condition2use = """WHERE{} "Minutes5UTC">='{}' AND "Minutes5UTC"<='{}' """.format(
        condition2use, start, end
    )

    query2use = (
        """SELECT "Minutes5UTC", "PriceArea", "ProductionLt100MW", "ProductionGe100MW","""
        + """ "OffshoreWindPower", "OnshoreWindPower", "SolarPower","""
        + """ "ExchangeGreatBelt", "ExchangeGermany","ExchangeNetherlands", "ExchangeNorway","""
        + """ "ExchangeSweden",	"BornholmSE4" """
        + """FROM "electricityprodex5minrealtime" """
        + condition2use
        + ' ORDER BY "Minutes5UTC" ASC'
    )

    dict2use = {
        "PriceArea": "price_area",
        "ProductionLt100MW": "generation_under_100MW",
        "ProductionGe100MW": "generation_over_100MW",
        "OffshoreWindPower": "offshore_wind_generation",
        "OnshoreWindPower": "onshore_wind_generation",
        "SolarPower": "solar_generation",
        "ExchangeGreatBelt": "import_from_great_belt",
        "ExchangeGermany": "import_from_germany",
        "ExchangeNetherlands": "import_from_netherlands",
        "ExchangeNorway": "import_from_norway",
        "ExchangeSweden": "import_from_sweden",
        "BornholmSE4": "import_from_sweden_to_bornholm",
    }

    data = __dk_energinet_dataservice_call(
        sql_query=query2use, output_format="Dataframe"
    )
    return format_to_timetable(
        data, time_column="Minutes5UTC", column_dict=dict2use, utc_index=True
    )


def electricity_spot_price(
    area="",
    start=None,
    end=None,
):
    if start is None:
        start = now() - timedelta(days=15)
    if end is None:
        end = now()

    start, end = __format_start_end(start, end)

    if area == "DK1":
        condition2use = """ "PriceArea" = 'DK1' AND"""

    elif area == "DK2":
        condition2use = """ "PriceArea" = 'DK2' AND"""

    else:
        condition2use = ""

    query2use = f"""SELECT "HourUTC", "SpotPriceEUR", "SpotPriceDKK", "PriceArea" FROM "elspotprices" WHERE{condition2use} "HourUTC">='{start}' AND "HourUTC"<='{end}'  ORDER BY "HourUTC" ASC"""

    dict2use = {
        "SpotPriceEUR": "spot_price_eur",
        "SpotPriceDKK": "spot_price_dkk",
        "PriceArea": "price_area",
    }

    data = __dk_energinet_dataservice_call(
        sql_query=query2use, output_format="Dataframe"
    )
    return format_to_timetable(
        data, time_column="HourUTC", column_dict=dict2use, utc_index=True
    )
