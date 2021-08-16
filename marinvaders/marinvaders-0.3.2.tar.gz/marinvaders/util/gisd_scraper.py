"""
Script do download and parse GISD web page to find distribution of species.

The data from GISD does provides additional information on alien ranges
for certain species. It also serves to confirm some of the
findings in the other databases.

The runtime of the script is around 30min and the result is saved in json
format. The filepath and -name must be specified when calling the script, e.g.

    python gisd_scraper /tmp/gisd_data.json

Alternatively, the module can be imported and used by

    import marinvaders.util
    marinvaders.util.get_gisd('/tmp/gisd_data.json')


"""

import datetime
import logging
import time
import sys
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def _remove_dots(obj):
    """Recursively remove any periods in dict keys"""
    if isinstance(obj, list):
        for index, value in enumerate(obj):
            if isinstance(value, dict) or isinstance(value, list):
                obj[index] = _remove_dots(value)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, dict) or isinstance(value, list):
                obj[key] = _remove_dots(value)
            new_key = key.replace(".", "_")
            if new_key != key:
                obj[new_key] = obj[key]
                del obj[key]
    return obj


def _process_species(species, retried=0):
    try:
        url = "http://www.iucngisd.org/gisd/speciesname/{}".format(
            species["Species"].replace(" ", "+")
        )
        species_page = requests.get(url)
        if species_page.status_code != 200:
            logging.warning(
                "Bad HTTP response for {}: {}".format(
                    species["Species"], species_page.status_code
                )
            )
        else:
            soup = BeautifulSoup(species_page.text, "html.parser")

            general_impacts = ""
            try:
                for content in (
                    soup.find("div", id="spe-general-title")
                    .find_next_sibling("div")
                    .contents
                ):
                    general_impacts += str(content)
            except Exception as e:
                logging.info("No general impacts div for {}".format(species["Species"]))
                logging.debug("Impact missing due to {}".format(e))

            species["General_impacts"] = general_impacts

            native_range = []
            for nr in (
                soup.find("div", id="nr-title").find_next_sibling("ul").find_all("li")
            ):
                native_range.append(nr.string.strip())

            alien_range = []
            for ar in (
                soup.find("div", id="ar-title").find_next_sibling("ul").find_all("li")
            ):
                sc, nlc = ar["id"].split("*")
                loc_per_country = requests.get(
                    "http://www.iucngisd.org/gisd/function/species_location.php?sc={}&nlc={}".format(
                        sc, nlc
                    )
                )
                for location in loc_per_country.json():
                    dc = location["distribution_code"]
                    payload = {"sc": sc, "dc": dc}
                    species_loc_main = requests.get(
                        "http://www.iucngisd.org/gisd/function/species_location_2.php",
                        params=payload,
                    ).json()
                    species_loc_imp = requests.get(
                        "http://www.iucngisd.org/gisd/function/species_location_4.php",
                        params=payload,
                    ).json()
                    if len(species_loc_main) > 1 or len(species_loc_imp) > 1:
                        logging.warning(
                            "specie_loc returns for {} in {} are longer than 1".format(
                                species["Species"], location["location_name"]
                            )
                        )
                        logging.info(species_loc_main)
                        logging.info(species_loc_imp)

                    if (
                        species_loc_main
                        and "name" in species_loc_main[0]
                        and "location_name" in species_loc_main[0]
                    ):
                        alien_range.append(species_loc_main[0])
                        # country = species_loc_main[0]["name"].strip()
                        # location = species_loc_main[0]["location_name"].strip()
                        # if location not in alien_range:
                        #     alien_range[location] = {}
                        # alien_range[location] = {}
                        # species_loc = alien_range[location]
                        # species_loc["species_loc_main"] = species_loc_main[0]
                        # if species_loc_imp:
                        #     species_loc["species_loc_imp"] = species_loc_imp[0]
                        # species_loc["species_loc_man"] = species_loc_man
                    else:
                        logging.info("Insufficient information to save species_loc")

    except ConnectionError:
        if retried < 3:
            time.sleep(1)
            return _process_species(species, retried=retried + 1)
        else:
            logging.error("Too many retries")
    except Exception as e:
        logging.error(e)

    # return remove_dots(species)
    return general_impacts, native_range, alien_range


def get_gisd(saveas):
    """Download, clean and save gisd data

    Source: http://www.iucngisd.org/gisd/

    Note
    ----
    GISD and IUCN in general apply a very strict licence on their data.
    You are not allowed to distribute the data downloaded by this script.
    Please check their terms and conditions for furter information.

    Parameters
    -----------
    saveas: str or pathlib.Path
        Path and filename for storing the data

    """

    starttime = time.perf_counter()
    logging.basicConfig(level=logging.INFO)
    filepath = Path(saveas)

    logging.info("Requesting summary data from iucn-gisd")
    r = requests.get("http://www.iucngisd.org/gisd/export_csv.php")

    logging.info("Parsing iucn-gisd data")
    lines = r.text.splitlines()
    firstline = [word.strip('"') for word in lines[0].split(";") if word != ""]
    species_list = []
    for line in lines[1:]:
        line = [word.strip('"') for word in line.split(";") if word != ""]
        species_list.append({firstline[i]: line[i] for i in range(len(firstline))})

    # Filtering the list to include only certain systems
    species_list = [
        {key: value for key, value in species.items()}
        for species in species_list
        if species["System"] in ["Marine", "Brackish", "Marine_freshwater_brackish"]
    ]

    logging.info("Requesting species data from iucn-gisd")
    json_output = {}
    json_output["processing_timestamp"] = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    gisd = []
    for species in tqdm(species_list):
        general_impacts, native_range, alien_range = _process_species(species)
        species["general_impacts"] = general_impacts
        species["native_range"] = native_range
        species["alien_range"] = alien_range

        gisd.append(species)

    df = pd.DataFrame(gisd)

    logging.info(f"Saveing gisd data to {filepath}")
    df.to_json(filepath)
    endtime = time.perf_counter()
    logging.info(f"Done. Total runtime {endtime-starttime} sec.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise TypeError("Specify filename with full path for saving the gisd data")
    get_gisd(sys.argv[1])
