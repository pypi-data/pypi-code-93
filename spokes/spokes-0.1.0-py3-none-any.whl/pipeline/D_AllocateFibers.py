import random
import numpy
import h5py
import time
from ..utils import logger

def allocate_fibers(databank_path):

	start_time = time.perf_counter()

	log = logger.get_logger(__name__)


	log.info("=============================")
	log.info("Allocating Fibers")
	log.info("=============================\n")


	with h5py.File(databank_path, 'a') as db:
		survey_selection_flag = db['/Galaxies/survey_selection_flag'][()]

		Nfibers = db['/Instrument/Fibers/nb_fibers'][()]

		verbose = db['/RuntimeParameters/verbose'][()]

	if 3 in verbose:
		log.setLevel(10)

	log.verbose(f"Imported data from databank at {databank_path}")

	Ngal = len(survey_selection_flag)

	log.verbose(f"Number of galaxies imported: {Ngal}")

	random.seed(9999)
	keep_fraction = 0.8

	Nsub = int(Ngal*keep_fraction)

	log.verbose(f"Fraction of galaxies selected: {keep_fraction}")
	log.verbose(f"Number of galaxies being selected: {Nsub}")
	log.verbose(f"Generating fiber selection flag...")

	fiber_selection_flag = numpy.empty(Ngal, dtype=bool)

	selected = random.sample(list(numpy.arange(Ngal)), Nsub)

	fiber_selection_flag[selected] = True

	fiber_selection_flag = survey_selection_flag * fiber_selection_flag

	log.verbose("Fiber selection flag generated")
	log.verbose(f"Total selected galaxies from combined selection flag: {numpy.count_nonzero(fiber_selection_flag)}")
	log.verbose(f"Generating fiber ID list for galaxies...")

	fiber_selection_id = numpy.nonzero(fiber_selection_flag)[0]
	fiber_id = numpy.full(Ngal, -1)
	fiber_id[fiber_selection_id] = numpy.array([random.randint(0, Nfibers-1) for r in range(len(fiber_selection_id))])

	log.verbose(f"Fiber ID list for galaxies generated")

	with h5py.File(databank_path, 'a') as db:
			db['/Galaxies/fiber_selection_flag'] = fiber_selection_flag
			db['/Galaxies/fiber_id'] = fiber_id

	log.verbose("Data written back to databank")

	end_time = time.perf_counter()
	log.verbose(f"Allocated fibers in {end_time - start_time} seconds")

if __name__ == "__main__":
	allocate_fibers("../data/data_bank.h5")
