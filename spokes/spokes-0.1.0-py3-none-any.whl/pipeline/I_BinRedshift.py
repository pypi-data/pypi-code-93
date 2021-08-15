import numpy
import h5py
import time
from ..utils import logger

def bin_redshift(databank_path):

    start_time = time.perf_counter()

    log = logger.get_logger(__name__)


    log.info("=============================")
    log.info("Bin Redshifts")
    log.info("=============================\n")


    with h5py.File(databank_path, 'a') as db:
        z_spec = db['/Galaxies/redshift_spectroscopic_spokes'][()]
        z_true = db['/Galaxies/z_true'][()]
        nbins = db['/AnalysisChoices/RedshiftBinning/nb_bins'][()]

        elg_flag = db['/Galaxies/elg_flag'][()]
        lrg_flag = db['/Galaxies/lrg_flag'][()]

        verbose = db['/RuntimeParameters/verbose'][()]

    if 8 in verbose:
        log.setLevel(10)

    log.verbose(f"Imported data from databank at {databank_path}")
    log.verbose(f"Generating spectroscopic redshift success flag and cropping z_spce, z_true, elg_flag, and lrg_flag...")

    zspec_success_flag = numpy.logical_or(elg_flag, lrg_flag)
    z_spec = z_spec[zspec_success_flag]
    z_true= z_true[zspec_success_flag]
    elg_flag = elg_flag[zspec_success_flag]
    lrg_flag = lrg_flag[zspec_success_flag]

    good_flag = (z_spec != -1)
    z_spec = z_spec[good_flag]
    z_true = z_true[good_flag]

    log.verbose(f"Cropped lists")
    log.verbose(f"Generating histograms...")

    hist_spec, bin_edges_spec = numpy.histogram(z_spec, nbins)
    width_spec = numpy.diff(bin_edges_spec)
    center_spec = [numpy.mean([bin_edges_spec[i], bin_edges_spec[i+1]]) for i in range(nbins)]

    hist_true, bin_edges_true = numpy.histogram(z_true, nbins)
    width_true = numpy.diff(bin_edges_true)
    center_true = [numpy.mean([bin_edges_true[i], bin_edges_true[i+1]]) for i in range(nbins)]

    log.verbose(f"Histograms generated")

    with h5py.File(databank_path, 'a') as db:
        db["/Ensemble/width_spec"] = width_spec
        db["/Ensemble/center_spec"] = center_spec
        db["/Ensemble/nbins_spec"] = nbins
        db["/Ensemble/bin_edge_spec"] = bin_edges_spec
        db["/Ensemble/histogram_redshift_spec"] = hist_spec

        db["/Ensemble/width_true"] = width_true
        db["/Ensemble/center_true"] = center_true
        db["/Ensemble/nbins_true"] = nbins
        db["/Ensemble/bin_edge_true"] = bin_edges_true
        db["/Ensemble/histogram_redshift_true"] = hist_true

        db["/Ensemble/histogram_redshift_spec_normalized"] = hist_spec/float(len(z_spec))
        db["/Ensemble/histogram_redshift_true_normalized"] = hist_true/float(len(z_true))

        db["/Ensemble/ngal_observed"] = len(z_spec)

    log.verbose("Data written back to databank")

    end_time = time.perf_counter()
    log.verbose(f"Binned redshift in {end_time - start_time} seconds")

if __name__ == "__main__":
    bin_redshift("../data/data_bank.h5")
