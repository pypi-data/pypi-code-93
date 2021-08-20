import logging
import json
import os

# Extract given field from json dictonary
def get_field_from_json(data, field):
    try:
        if not data[field]:
            raise Exception(f"Required 'bic-meta.json' field: {field} is empty.")
        else:
            logging.info(f"\tFound field: {field}")
        return data[field]
    except KeyError:
        raise Exception(f"'bic-meta.json' does not contain a required field: {field}")


# Verify whether AIU and AIC directories exists
def verify_directory_structure(path):
    logging.info("Verifying directory structure")

    data_path = os.path.join(path, "data")
    if not os.path.exists(data_path):
        raise Exception("Directory named 'data' does not exist.")

    id = None
    aic_folder = None
    for dir in os.listdir(data_path):
        dir_path = os.path.join(data_path, dir)
        if os.path.isdir(dir_path):
            data = dir.split("::")
            current_id = data[0]
            if not id:
                id = current_id
            elif id != current_id:
                raise Exception("Ids does not match in directory names.")

            is_aic = False
            empty = True
            for sub in os.listdir(dir_path):
                empty = False
                if "bic-meta.json" in sub:
                    is_aic = True

            if empty:
                raise Exception(f"Empty directory found: {dir_path}")

            if is_aic:
                aic_folder = dir_path
                logging.info(f"\tFound AIC file directory: {dir_path}")
            else:
                logging.info(f"\tFound AIU file directory: {dir_path}")

    if not aic_folder:
        raise Exception("AIC directory was not found.")

    return aic_folder


# Check whether bic-meta.json contains the required fields
def validate_bic_meta(path, aic_folder):
    logging.info("Validating bic-meta.json")
    try:
        with open(os.path.join(aic_folder, "bic-meta.json")) as json_file:
            data = json.load(json_file)

            required_fields = ["metadataFile_upstream", "contentFiles"]
            for field in required_fields:
                get_field_from_json(data, field)

    except FileNotFoundError:
        raise Exception("bic-meta.json file not found.")


# Validate data according to the CERN AIP specification
def validate_aip(path):
    logging.basicConfig(level=20, format="%(message)s")
    logging.info("Starting validation")

    try:
        aic_folder = verify_directory_structure(path)

        validate_bic_meta(path, aic_folder)

        logging.info("Validation ended successfully.")

        return {"status": 0, "errormsg": None}
    except Exception as e:
        logging.error(f"Validation failed with error: {e}")

        return {"status": 1, "errormsg": e}
