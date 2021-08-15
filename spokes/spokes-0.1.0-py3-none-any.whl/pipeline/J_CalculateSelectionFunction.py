import numpy
import h5py
import time
from ..utils import logger

def calculate_selection(databank_path):

    start_time = time.perf_counter()

    log = logger.get_logger(__name__)


    log.info("=============================")
    log.info("Calculate Selection")
    log.info("=============================\n")


    with h5py.File(databank_path, 'a') as db:
        dz_true_ini	= db['/AnalysisChoices/SelectionFunction/ztrue_resolution'][()]
        delta_dz = db['/AnalysisChoices/SelectionFunction/delta_ztrue_resolution'][()]
        z_spec = db['/Galaxies/redshift_spectroscopic_spokes'][()]
        z_true = db['/Galaxies/z_true'][()]

        elg_flag  = db['/Galaxies/elg_flag'][()]
        lrg_flag = db['/Galaxies/lrg_flag'][()]

        width = db['/Ensemble/width_spec'][()]
        center = db['/Ensemble/center_spec'][()]
        bin_edge = db['/Ensemble/bin_edge_spec'][()]
        hist = db['/Ensemble/histogram_redshift_spec'][()]

        verbose = db['/RuntimeParameters/verbose'][()]

    if 9 in verbose:
        log.setLevel(10)

    log.verbose(f"Imported data from databank at {databank_path}")
    log.verbose(f"Generating spectroscopic redshift success flag and cropping z_spce, z_true, elg_flag, and lrg_flag...")

    zspec_success_flag = numpy.logical_or(elg_flag, lrg_flag)
    z_true = z_true[zspec_success_flag]
    z_spec = z_spec[zspec_success_flag]

    good_flag = (z_spec != -1)
    z_spec = z_spec[good_flag]
    z_true = z_true[good_flag]

    log.verbose(f"Cropped lists")

    nbin_spec = len(center)

    center_true_temp = []
    hist_true_temp = []
    bin_edge_true_full = numpy.zeros((nbin_spec,2))
    dz_true_full = numpy.zeros(nbin_spec)
    nbin_true_full = numpy.zeros(nbin_spec)
    for i in range( nbin_spec ):

        # calculate bin size
        bin_size = bin_edge[i+1] - bin_edge[i]

        # cut spectroscopic redshifts
        cut_z_spec_lo = (z_spec > bin_edge[i])
        cut_z_spec_hi = (z_spec < bin_edge[i+1])
        cut_z_spec_tot = cut_z_spec_lo * cut_z_spec_hi #numpy.logical_and(cut_z_spec_lo, cut_z_spec_hi)

        # get true redshifts in this range
        z_true_temp	= z_true[cut_z_spec_tot]

        # reset resolution loop checker
        nbin_true_start = 100
        nbin_true_min = 10
        ngal_min = 10
        nbin_true = nbin_true_start
        check_nbin = True
        while check_nbin:
            # measure distribution
            hist_temp, bin_edge_temp = numpy.histogram(z_true_temp, nbin_true)
            width_temp = numpy.diff(bin_edge_temp)
            center_temp = [numpy.mean([bin_edge_temp[i], bin_edge_temp[i+1]]) for i in range(nbin_true)]

            # count number of bins that have zero gals
            nbin_zero = len(numpy.where(hist_temp == 0))

            # check if bins at edges are zero
            zero_count_edge = 0
            if hist_temp[0]  == 0 :
            	zero_count_edge += 1
            if hist_temp[-1] == 0 :
            	zero_count_edge += 1

            # compare total zero count to edge zero count
            if nbin_zero == zero_count_edge:	# if total zero count is equal to edge zero count: if only zeros are at edge ...
            	if min(hist_temp[numpy.where(hist_temp != 0)[0]]) >= ngal_min: # if smallest hist bin has more than the minimum ...
            		check_nbin = False
            	else:
            		nbin_true -= 1
            else:
            	nbin_true-=1

            # if we reach minimum nbin_true, then just punt: there aren't enough galaxies
            if nbin_true < nbin_true_min:
                check_nbin = False
                log.info('There are not enough galaxies to meet the prescription of the minimum number of true bins and minimum number of galaxies per true bin')
                log.info('Algorithm will not simply produce a distribution at the minimum number of true bins, regardless distribution shape and content')
                log.info('Could optionally produce prescribed continuous function -- e.g., gaussian')


        # add to 2d matrix
        center_true_temp.append(numpy.array(center_temp))
        hist_true_temp.append(numpy.array(hist_temp))

        # add info to bin edges
        bin_edge_true_full[i,:] = bin_edge_temp[0], bin_edge_temp[-1]

        # record info for bin number and resolution value
        #dz_true_full[i]	 = dz_true
        nbin_true_full[i] = nbin_true

    # create 2-dimensional array; with information from biggest row
    center_true_full = numpy.zeros( (int(nbin_spec), int(max(nbin_true_full)+1) ) )
    hist_true_full   = numpy.zeros( (int(nbin_spec), int(max(nbin_true_full)+1 )) )

    # loop over uber-bins
    for i in range( nbin_spec ):
        center_true_full[i, 0:int(nbin_true_full[i]) +1] = center_true_temp[i]
        hist_true_full[i, 0:int(nbin_true_full[i]) +1  ] = hist_true_temp[i]

    # write redshift bins
    with h5py.File(databank_path, 'a') as db:
        db['/Ensemble/Selection/nbins_ztrue']		= nbin_true_full
        db['/Ensemble/Selection/bin_edge_ztrue']	= bin_edge_true_full
        db['/Ensemble/Selection/hist_ztrue']		= hist_true_full
        db['/Ensemble/Selection/center_ztrue']		= center_true_full

    log.verbose("Data written back to databank")

    end_time = time.perf_counter()
    log.verbose(f"Calculated selection function in {end_time - start_time} seconds")

if __name__ == "__main__":
    calculate_selection("../data/data_bank.h5")
