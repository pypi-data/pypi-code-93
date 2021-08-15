import os
import importlib
import yaml
import time
from .pipeline import *
from .utils import logger

def run_simulation(experiment_parameters_path):

    simulation_start_time = time.perf_counter()

    with open(experiment_parameters_path) as experiment_parameters_file:
        experiment_parameters = yaml.safe_load(experiment_parameters_file)

    Prerun = experiment_parameters["PrerunParameters"]

    order = Prerun["order"]
    databank_path = Prerun["data_bank"]
    duplicate = Prerun["duplicate_data_bank"]
    log_dir = Prerun["log_dir"]

    logger_name = "spokes"
    log, log_file = logger.setup_spokes_logger(logger_name, log_dir)

    log.info(f"Prerun parameters imported succesfully")
    log.info(f"Source data bank:            {databank_path}")
    log.info(f"Duplicating data bank:       {duplicate}")
    log.info(f"Logging to file:             {log_file}")
    log.info(f"Running simulation in order: {order}")
    log.info(f"Starting simulation...")

    user_units = experiment_parameters['User-createdUnits']

    for unit_num in order:
        if unit_num == 0:
            if user_units["Setup"] == "Default":
                log.info(f"Running Setup unit...")
                if duplicate:
                    log.info(f"Duplicating data bank")
                    databank_path = A_Setup.duplicate_databank(experiment_parameters_path, databank_path)
                    log.info(f"Data bank duplicated succesfully")
                log.info(f"Importing Parameters...")
                A_Setup.import_parameters(experiment_parameters_path, databank_path)
                log.info(f"Parameters imported succesfully")
                log.info(f"Setup unit completed succesfully")
            else:
                log.info(f"Running user-created Setup unit...")
                mod = importlib.import_module(user_units["Setup"])
                if duplicate:
                    log.info(f"Duplicating data bank")
                    databank_path = mod.duplicate_databank(experiment_parameters_path, databank_path)
                    log.info(f"Data bank duplicated succesfully")
                log.info(f"Importing Parameters...")
                mod.import_parameters(experiment_parameters_path, databank_path)
                log.info(f"Parameters imported succesfully")
                log.info(f"User-created Setup unit completed succesfully")

        elif unit_num == 1:
            if user_units["SelectTargets"] == "Default":
                log.info(f"Running Select Targets unit...")
                B_SelectTargets.select_targets(databank_path)
                log.info(f"Select Targets unit completed succesfully")
            else:
                log.info(f"Running user-created Select Targets unit...")
                mod = importlib.import_module(user_units["SelectTargets"])
                mod.select_targets(databank_path)
                log.info(f"User-created Select Targets unit completed succesfully")

        elif unit_num == 2:
            if user_units["TileSurvey"] == "Default":
                log.info(f"Running Tile Survey unit...")
                C_TileSurvey.tile_survey(databank_path)
                log.info(f"Tile Survey unit completed succesfully")
            else:
                log.info(f"Running user-created Tile Survey unit...")
                mod = importlib.import_module(user_units["TileSurvey"])
                mod.tile_survey(databank_path)
                log.info(f"User-created Tile Survey unit completed succesfully")

        elif unit_num == 3:
            if user_units["AllocateFibers"] == "Default":
                log.info(f"Running Allocate Fibers unit...")
                D_AllocateFibers.allocate_fibers(databank_path)
                log.info(f"Allocate Fibers unit completed succesfully")
            else:
                log.info(f"Running user-created Allocate Fibers unit...")
                mod = importlib.import_module(user_units["AllocateFibers"])
                mod.allocate_fibers(databank_path)
                log.info(f"User-created Allocate Fibers unit completed succesfully")

        elif unit_num == 4:
            if user_units["CalculateThroughput"] == "Default":
                pass
            else:
                log.info(f"Running user-created Calculate Throughput unit...")
                mod = importlib.import_module(user_units["CalculateThroughput"])
                mod.allocate_fibers(databank_path)
                log.info(f"User-created Calculate Throughput unit completed succesfully")

        elif unit_num == 5:
            if user_units["SimulateSpectrum"] == "Default":
                pass
            else:
                log.info(f"Running user-created Simulate Spectrum unit...")
                mod = importlib.import_module(user_units["SimulateSpectrum"])
                mod.allocate_fibers(databank_path)
                log.info(f"User-created Simulate Spectrum unit completed succesfully")

        elif unit_num == 6:
            if user_units["GenerateSpectrumNoise"] == "Default":
                pass
            else:
                log.info(f"Running user-created Generate Spectrum Noise unit...")
                mod = importlib.import_module(user_units["GenerateSpectrumNoise"])
                mod.allocate_fibers(databank_path)
                log.info(f"User-created Generate Spectrum Noise unit completed succesfully")

        elif unit_num == 7:
            if user_units["MeasureRedshift"] == "Default":
                log.info(f"Running Measure Spectroscopic Redshift unit...")
                H_MeasureSpectroscopicRedshift.measure_redshift(databank_path)
                log.info(f"Measure Spectroscopic Redshift unit completed succesfully")
            else:
                log.info(f"Running user-created Measure Spectroscopic Redshift unit...")
                mod = importlib.import_module(user_units["MeasureRedshift"])
                mod.measure_redshift(databank_path)
                log.info(f"User-created Measure Spectroscopic Redshift unit completed succesfully")

        elif unit_num == 8:
            if user_units["BinRedshift"] == "Default":
                log.info(f"Running Bin Redshift unit...")
                I_BinRedshift.bin_redshift(databank_path)
                log.info(f"Bin Redshift unit completed succesfully")
            else:
                log.info(f"Running user-created Bin Redshift unit...")
                mod = importlib.import_module(user_units["BinRedshift"])
                mod.bin_redshift(databank_path)
                log.info(f"User-created Bin Redshift unit completed succesfully")

        elif unit_num == 9:
            if user_units["CalculateSelectionFunction"] == "Default":
                log.info(f"Running Calculate Selection Function unit...")
                J_CalculateSelectionFunction.calculate_selection(databank_path)
                log.info(f"Calculate Selection Function unit completed succesfully")
            else:
                log.info(f"Running user-created Calculate Selection Function unit...")
                mod = importlib.import_module(user_units["CalculateSelectionFunction"])
                mod.calculate_selection(databank_path)
                log.info(f"User-created Calculate Selection Function unit completed succesfully")

        elif unit_num == 10:
            if user_units["EstimateCosmologyParameters"] == "Default":
                pass
            else:
                log.info(f"Running user-created Estimate Cosmology Parameters unit...")
                mod = importlib.import_module(user_units["EstimateCosmologyParameters"])
                mod.allocate_fibers(databank_path)
                log.info(f"User-created Estimate Cosmology Parameters unit completed succesfully")

        elif unit_num == 11:
            if user_units["ReportResults"] == "Default":
                pass
            else:
                log.info(f"Running user-created Report Results Noise unit...")
                mod = importlib.import_module(user_units["ReportResults"])
                mod.allocate_fibers(databank_path)
                log.info(f"User-created Report Results unit completed succesfully")

    simulation_end_time = time.perf_counter()

    log.info(f"Simulation completed in {simulation_end_time - simulation_start_time} seconds")

if __name__ == "__main__":
    run_simulation("config_temp/experiment_parameters.yml")
