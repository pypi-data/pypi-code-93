import numpy
import h5py
import time
from ..utils import logger

def select_targets(databank_path):

    start_time = time.perf_counter()

    log = logger.get_logger(__name__)


    log.info("=============================")
    log.info("Selecting Targets")
    log.info("=============================\n")


    #Retrieve data from hdf5 file
    with h5py.File(databank_path, 'a') as db:

        # import target selection parameters
        dummyMagCutRange	   = db['/AnalysisChoices/TargetSelection/dummy_magcut_range'][()]
        elg_linear_cuts_coeffs = db['/AnalysisChoices/TargetSelection/elg_linear_cuts_coeffs'][()]
        elg_linear_cuts_connector = db['/AnalysisChoices/TargetSelection/elg_linear_cuts_connector'][()]
        lrg_linear_cuts_coeffs = db['/AnalysisChoices/TargetSelection/lrg_linear_cuts_coeffs'][()]
        lrg_linear_cuts_connector = db['/AnalysisChoices/TargetSelection/lrg_linear_cuts_connector'][()]

        # import mags and photo-zs from target cat
        magnitude_u = db['/Galaxies/magnitude_u'][()]
        magnitude_g = db['/Galaxies/magnitude_g'][()]
        magnitude_r = db['/Galaxies/magnitude_r'][()]
        magnitude_i = db['/Galaxies/magnitude_i'][()]
        magnitude_z = db['/Galaxies/magnitude_z'][()]
        magnitude_y = db['/Galaxies/magnitude_y'][()]
        magnitude_hh = db['/Galaxies/magnitude_hh'][()]

        photo_z = db['/Galaxies/redshift_photometric'][()]

        verbose = db['/RuntimeParameters/verbose'][()]

    if 1 in verbose:
        log.setLevel(10)

    log.verbose(f"Imported data from databank at {databank_path}")

    # count number of galaxies
    Ngal = len(magnitude_y)

    log.verbose(f"Number of galaxies imported: {Ngal}")

    # set new variable names for values for imported quantities
    dummy_magcut_min = dummyMagCutRange[0]
    dummy_magcut_max = dummyMagCutRange[1]

    elg_linear_cuts_coeffs = numpy.matrix(elg_linear_cuts_coeffs)
    lrg_linear_cuts_coeffs = numpy.matrix(lrg_linear_cuts_coeffs)

    log.verbose(f"Performing dummy cuts with magnitude range [{dummy_magcut_min}, {dummy_magcut_max}]...")

    # set cuts for 'dummy' values
    dummycut_u_flag = (magnitude_u < dummy_magcut_max)*(magnitude_u > dummy_magcut_min)
    dummycut_g_flag = (magnitude_g < dummy_magcut_max)*(magnitude_g > dummy_magcut_min)
    dummycut_r_flag = (magnitude_r < dummy_magcut_max)*(magnitude_r > dummy_magcut_min)
    dummycut_i_flag = (magnitude_i < dummy_magcut_max)*(magnitude_i > dummy_magcut_min)
    dummycut_z_flag = (magnitude_z < dummy_magcut_max)*(magnitude_z > dummy_magcut_min)
    dummycut_y_flag = (magnitude_y < dummy_magcut_max)*(magnitude_y > dummy_magcut_min)
    dummycut_hh_flag = (magnitude_hh < dummy_magcut_max)*(magnitude_hh > dummy_magcut_min)
    dummycut_flag = dummycut_u_flag*dummycut_g_flag*dummycut_r_flag*dummycut_i_flag*dummycut_z_flag*dummycut_y_flag

    log.verbose(f"Dummy cuts performed")

    # ELG selection
    if (elg_linear_cuts_coeffs.size != 0):

        log.verbose(f"Performing ELG linear cuts...")

        magsz_matrix = numpy.matrix([numpy.ones(magnitude_g.shape),\
                                    magnitude_u,magnitude_g,magnitude_r,magnitude_i,magnitude_z,magnitude_y,\
                                    magnitude_hh,photo_z])

    	# perform linear cuts
        b = elg_linear_cuts_coeffs * magsz_matrix
        elg_linear_cuts_flag_list = (b < 0)

        if (elg_linear_cuts_connector == "union"):
            log.verbose(f"ELG linear cuts connector: 'union'")
            elg_flag = numpy.array((numpy.min(b,0) < 0))[0]

        elif (elg_linear_cuts_connector == "intersection"):
            log.verbose(f"ELG linear cuts connector: 'intersection'")
            elg_flag = numpy.array((numpy.max(b,0) < 0))[0]

        else:
            log.critical(f"unknown connector between ELG linear cuts")
            raise IOError("unknown connector between ELG linear cuts")

        log.verbose(f"ELG: {numpy.sum(elg_flag)}")
        log.verbose(f"Performed ELG cuts")

    else:
        elg_flag = numpy.ones(magnitude_g.shape).astype(bool)


    # LRG selection
    if (lrg_linear_cuts_coeffs.size != 0):

        log.verbose(f"Performing LRG linear cuts...")

        magsz_matrix = numpy.matrix([numpy.ones(magnitude_g.shape),\
                                    magnitude_u,magnitude_g,magnitude_r,magnitude_i,magnitude_z,magnitude_y,\
                                    magnitude_hh,photo_z])

        # perform linear cuts
        b = lrg_linear_cuts_coeffs * magsz_matrix
        lrg_linear_cuts_flag_list = (b < 0)

        if (lrg_linear_cuts_connector == "union"):
            log.verbose(f"LRG linear cuts connector: 'union'")
            lrg_flag = numpy.array((numpy.min(b,0) < 0))[0]

        elif (lrg_linear_cuts_connector == "intersection"):
            log.verbose(f"LRG linear cuts connector: 'intersection'")
            lrg_flag = numpy.array((numpy.max(b,0) < 0))[0]

        else:
            log.critical(f"unknown connector between LRG linear cuts")
            raise IOError("unknown connector between LRG linear cuts")

        log.verbose(f"LRG: {numpy.sum(lrg_flag)}")
        log.verbose(f"Performed LRG cuts")

    else:
        lrg_flag = numpy.ones(magnitude_g.shape).astype(bool)


    #Combine elg and lrg flags
    target_selection_flag  = elg_flag + lrg_flag

    log.verbose(f"Computed target selection flag")

    # exporting selection flags
    with h5py.File(databank_path, 'a') as db:
        db['/Galaxies/dummycut_flag'] = dummycut_flag
        db['/Galaxies/elg_flag_list'] = elg_linear_cuts_flag_list
        db['/Galaxies/elg_flag'] = elg_flag
        db['/Galaxies/lrg_flag_list'] = lrg_linear_cuts_flag_list
        db['/Galaxies/lrg_flag'] = lrg_flag
        db['/Galaxies/target_selection_flag'] = target_selection_flag

    log.verbose("Data written back to databank")
    log.verbose(f"*********************************")
    log.verbose(f"Target selection results summary:")

    #Sumarizing results
    Ngal = len(magnitude_g)
    elg_selected = numpy.sum((elg_flag == True))
    lrg_selected = numpy.sum((lrg_flag == True))
    selected = numpy.sum((target_selection_flag == True))
    elg_discarded = numpy.sum((elg_flag == False))
    lrg_discarded = numpy.sum((lrg_flag == False))
    discarded = numpy.sum((target_selection_flag == False))
    undefined = len(magnitude_g) - selected - discarded

    log.verbose(f"ELG selected:    {elg_selected}")
    log.verbose(f"ELG discarded:   {elg_discarded}")
    log.verbose(f"LRG selected:    {lrg_selected}")
    log.verbose(f"LRG discarded:   {lrg_discarded}")
    log.verbose(f"total selected:  {selected}")
    log.verbose(f"total discarded: {discarded}")
    log.verbose(f"undefined:       {undefined}")
    log.verbose(f"===========================")
    log.verbose(f"total:           {Ngal}")

    if (undefined == 0):
        log.verbose(f"*** Checksum Passed ***")
    else:
        log.warning(f"XXX CHECKSUM FAILED XXX")
    log.verbose(f"*********************************")

    end_time = time.perf_counter()
    log.verbose(f"Selected targets in {end_time - start_time} seconds")
