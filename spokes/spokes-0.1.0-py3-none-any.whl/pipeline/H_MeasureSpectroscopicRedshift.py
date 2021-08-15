import random
import numpy
import h5py
import time
from ..utils import logger

def measure_redshift(databank_path):

    start_time = time.perf_counter()

    log = logger.get_logger(__name__)


    log.info("=============================")
    log.info("Measuring Redshift")
    log.info("=============================\n")


    with h5py.File(databank_path, 'a') as db:
        z_true = db['/Galaxies/z_true'][()]
        fiber_selection_flag = db['/Galaxies/fiber_selection_flag'][()]

        verbose = db['/RuntimeParameters/verbose'][()]

    if 7 in verbose:
        log.setLevel(10)

    log.verbose(f"Imported data from databank at {databank_path}")

    Ngal = len(fiber_selection_flag)

    log.verbose(f"Number of galaxies imported: {Ngal}")

    z_true = numpy.array(z_true)

    log.verbose(f"Cropping true redshift...")

    z_true_cropped = z_true[fiber_selection_flag]

    log.verbose(f"True redshift cropped")
    log.verbose(f"Adding random error to true redshift...")

    error = numpy.random.uniform(0.98, 1.02, len(z_true_cropped))

    z_spec = z_true_cropped * error

    log.verbose(f"Added random error to true redshift")
    log.verbose(f"Generating redshift_spectroscopic_spokes_full...")

    redshift_spectroscopic_spokes_full = numpy.full(Ngal, -1)
    redshift_spectroscopic_spokes_full[fiber_selection_flag] = z_spec

    log.verbose(f"redshift_spectroscopic_spokes_full generated")

    with h5py.File(databank_path, 'a') as db:
        db['/Galaxies/redshift_spectroscopic_spokes'] = redshift_spectroscopic_spokes_full

    log.verbose("Data written back to databank")

    end_time = time.perf_counter()
    log.verbose(f"Measured redshift in {end_time - start_time} seconds")

if __name__ == "__main__":
    measure_redshift("../data/data_bank.h5")
