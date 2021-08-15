import yaml
import h5py
import numpy
import time
from datetime import datetime
import os
from ..utils import logger

def duplicate_databank(experiment_parameters_path, databank_path):

    start_time = time.perf_counter()

    log = logger.get_logger(__name__)


    log.info("=============================")
    log.info("Duplicating Data bank")
    log.info("=============================\n")


    with open(experiment_parameters_path) as experiment_parameters_file:
        experiment_parameters = yaml.safe_load(experiment_parameters_file)

    if 0 in experiment_parameters["RuntimeParameters"]["verbose"]:
        log.setLevel(10)

    log.verbose(f"Duplicating data bank at {databank_path}")

    new_filename = datetime.now().strftime("data_bank_%d_%m_%Y_%H_%M_%S.h5")
    dirname = os.path.dirname(databank_path)
    new_path = os.path.join(dirname, new_filename)

    log.verbose(f"New data bank created at {new_path}")
    log.verbose(f"Copying Galaxies data to new data bank...")

    db_old = h5py.File(databank_path, 'a')
    db_new = h5py.File(new_path, 'a')
    db_old.copy("Galaxies", db_new)
    db_old.close(); db_new.close()

    log.verbose(f"Data copied to {new_path}")

    end_time = time.perf_counter()
    log.verbose(f"Duplicated data bank in {end_time - start_time} seconds")

    return new_path

def import_parameters(experiment_parameters_path, databank_path):

    start_time = time.perf_counter()

    log = logger.get_logger(__name__)


    log.info("=============================")
    log.info("Importing Parameters")
    log.info("=============================\n")


    with open(experiment_parameters_path) as experiment_parameters_file:
        experiment_parameters = yaml.safe_load(experiment_parameters_file)

    if 0 in experiment_parameters["RuntimeParameters"]["verbose"]:
        log.setLevel(10)

    log.verbose(f"Loaded eperiment paramters from {experiment_parameters_path}")

    with h5py.File(databank_path, 'a') as db:

        log.verbose(f"Opened databank h5 file at {databank_path}")

        data_groups = ["AnalysisChoices", "Constants", "Environment", "Fibers", "Instrument", "Ensemble", "RuntimeParameters", "SpectralTemplates", "SurveyTiles", "SurveyParameters"]
        for data_group in data_groups:
            db.create_group(data_group)

        log.verbose(f"Created data groups in databank: {data_groups}")

        parameter_group_location = {
            "RuntimeParameters": "/RuntimeParameters/",
            "Fibers": "/Instrument/Fibers/",
            "Telescope": "/Instrument/Telescope/",
            "Spectrograph": "/Instrument/Spectrograph/",
            "SurveyParameters": "/SurveyParameters/",
            "Atmosphere": "/Environment/Atmosphere/",
            "TargetSelection": "/AnalysisChoices/TargetSelection/",
            "RedshiftBinning": "/AnalysisChoices/RedshiftBinning/",
            "Spectroscopy": "/AnalysisChoices/Spectroscopy/",
            "SelectionFunction": "/AnalysisChoices/SelectionFunction/",
            "Throughput": "/Throughput/",
            "Constants": "/Constants/"
        }

        for parameter_group in parameter_group_location:
            try:
                for dataset in experiment_parameters[parameter_group]:
                    try:
                        db[parameter_group_location[parameter_group] + dataset] = experiment_parameters[parameter_group][dataset]
                    except:
                        asciiEncode = [n.encode("ascii", "ignore") for n in experiment_parameters[parameter_group][dataset]]
                        db[parameter_group_location[parameter_group] + dataset] = asciiEncode
            except:
                pass

            log.verbose(f"Imported {parameter_group} paramters")

    log.verbose(f"All experiment paramters succesfully imported")

    end_time = time.perf_counter()
    log.verbose(f"Imported parameters in {end_time - start_time} seconds")
