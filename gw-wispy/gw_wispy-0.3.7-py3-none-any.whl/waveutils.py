import numpy as np
import h5py
from scipy.interpolate import InterpolatedUnivariateSpline as IUS
import phenom
from . import lalutils
import lal
import lalsimulation as lalsim
import configparser
import os
import glob


class SingleModeNRWaveform(object):
    def __init__(self, nrfile, ell, mm, dt, t1=None, t2=None):

        self.nrfile = nrfile
        self.dt = dt
        self.t1 = t1
        self.t2 = t2

        self.get_lm_mode(self.nrfile, ell, mm, self.dt)

    def get_lm_mode(self, nrfile, ell, mm, dt):

        if ".h5" in nrfile:
            f = h5py.File(nrfile, "r")

            self.q = f.attrs["mass1"] / f.attrs["mass2"]
            self.eta = f.attrs["eta"]

            amp_tmp = f["amp_l{0}_m{1}".format(ell, mm)]
            amp_x = amp_tmp["X"][()]
            amp_y = amp_tmp["Y"][()]

            phase_tmp = f["phase_l{0}_m{1}".format(ell, mm)]
            phase_x = phase_tmp["X"][()]
            phase_y = phase_tmp["Y"][()]

            f.close()
        else:
            # bam
            self.sim_dir = os.path.dirname(nrfile)
            self.bbh_file = glob.glob(os.path.join(self.sim_dir, "*.bbh"))[0]
            # strict=False because of DuplicateSectionError
            config = configparser.ConfigParser(strict=False)

            config.read(self.bbh_file)
            mass1_tmp = float(config["metadata"]["mass1"])
            mass2_tmp = float(config["metadata"]["mass2"])
            self.initial_sep = float(config["metadata"]["initial-separation"])

            if mass1_tmp >= mass2_tmp:
                mass1 = mass1_tmp
                mass2 = mass2_tmp
            else:
                mass1 = mass2_tmp
                mass2 = mass1_tmp

            self.mass1 = mass1
            self.mass2 = mass2
            self.mtot = self.mass1 + self.mass2
            self.q = self.mass1 / self.mass2
            self.eta = self.mass1 * self.mass2 / (self.mtot) ** 2.0

            times, re_hlm, im_hlm = np.loadtxt(nrfile, unpack=True)

            # SIGN CONVENTION HERE NOTE SURE WHAT IS CORRECT FOR BAM
            hlm = re_hlm - 1.0j * im_hlm

            amp_x = times
            amp_y = np.abs(hlm)

            phase_x = times
            phase_y = np.unwrap(np.angle(hlm))

        # shift so that amp peak is at t=0 - will need to be more careful with HMs
        amp_peak_idx = amp_y.argmax()
        amp_peak_time = amp_x[amp_peak_idx]
        amp_x = amp_x - amp_peak_time
        phase_x = phase_x - amp_peak_time

        amp_i = IUS(amp_x, amp_y)
        phase_i = IUS(phase_x, phase_y)

        if self.t1 is None:
            self.t1 = max(amp_x[0], phase_x[0])
        if self.t2 is None:
            self.t2 = min(amp_x[-1], phase_x[-1])

        # t1,t2=-600,100

        common_times = np.arange(self.t1, self.t2, dt)

        amplist = amp_i(common_times)
        phaselist = phase_i(common_times)

        self.times = common_times
        self.amp = amplist
        self.phi = phaselist
        # self.hlm["{0}, {1}".format(ell, mm)] = self.amp * np.exp(-1.j * self.phi)
        self.hlm = self.amp * np.exp(-1.0j * self.phi)

    def resample_data(self, new_time_array):
        """
        new_time_array : numpy.array

        redefines the amp, phi and hlm attributes to be sampled on
        the new_time_array
        """
        amp_i = IUS(self.times, self.amp)
        phi_i = IUS(self.times, self.phi)

        self.npts = len(new_time_array)
        self.times = new_time_array
        self.amp = amp_i(new_time_array)
        self.phi = phi_i(new_time_array)
        self.hlm = self.amp * np.exp(-1.0j * self.phi)


class NRStrain(object):
    """
    stores Psi4 data aligned such that the peak of Psi4 is at t=0
    """

    def __init__(self, nrfile, ell, mm, dt, t1, t2):
        self.nrfile = nrfile
        self.ell = ell
        self.mm = mm
        self.dt = dt
        self.t1 = t1
        self.t2 = t2

        self.nrdata = SingleModeNRWaveform(
            self.nrfile, self.ell, self.mm, self.dt, t1=self.t1, t2=self.t2
        )

        self.eta = self.nrdata.eta
        self.q = float("{:.2f}".format(self.nrdata.q))

        amp = self.nrdata.amp
        phase = self.nrdata.phi

        max_idx_amp = np.argmax(amp)
        time_shift = self.nrdata.times[max_idx_amp]

        new_times = self.nrdata.times - time_shift

        self.times = np.arange(self.t1, self.t2, self.dt)
        self.amp = IUS(new_times, amp)(self.times)
        self.phase = IUS(new_times, phase)(self.times)

        self.hlm = self.amp * np.exp(-1.0j * self.phase)

        eta, chi1z, chi2z = self.eta, 0.0, 0.0
        self.fin_spin = phenom.remnant.FinalSpin0815(eta, chi1z, chi2z)
        self.fring = phenom.remnant.fring(eta, chi1z, chi2z, self.fin_spin)
        self.fdamp = phenom.remnant.fdamp(eta, chi1z, chi2z, self.fin_spin)
        self.final_mass = 1.0 - phenom.EradRational0815(eta, chi1z, chi2z)


class WaveformGeneration(object):
    def __init__(
        self,
        approximant=None,
        f_min=20,
        t_min=-2000,
        t_max=100,
        dt=0.5,
        nrfile=None,
        q=None,
    ):
        self.approximant = approximant
        self.f_min = f_min
        self.t_min = t_min
        self.t_max = t_max
        self.dt = dt
        self.nrfile = nrfile
        self.q = q

        self.times = np.arange(self.t_min, self.t_max, self.dt)

        if self.nrfile:
            self.approximant_string = "NR"
            self.label = self.nrfile.split("/")[-1].split(".h5")[0]
            self.nrstrain = NRStrain(
                self.nrfile, 2, 2, self.dt, t1=self.t_min, t2=self.t_max
            )
            self.q = self.nrstrain.q
            times = self.nrstrain.times
            amp = self.nrstrain.amp
            phase = self.nrstrain.phase

            tpeak = lalutils.peak_align_shift(times, amp, npts=1e6, dx_npts=10)

            self.amp = IUS(times - tpeak, amp)(self.times)
            self.phase = IUS(times - tpeak, phase)(self.times)
            self.phase -= self.phase[0]
            self.freq = IUS(self.times, self.phase).derivative()(self.times)

            self.h22 = self.amp * np.exp(1.0j * self.phase)
            self.Reh22 = np.real(self.h22)
            self.Imh22 = np.imag(self.h22)

        else:
            self.approximant_string = lalsim.GetStringFromApproximant(self.approximant)
            self.label = lalsim.GetStringFromApproximant(self.approximant)
            mtotal = 20
            m1, m2 = phenom.m1_m2_M_q(mtotal, self.q)
            params = lalutils.gen_td_wf_params(
                m1=m1, m2=m2, approximant=self.approximant, f_min=self.f_min
            )
            times, amp, phase = lalutils.gen_td_wf(params, t_min=None, t_max=None)

            tpeak = lalutils.peak_align_shift(times, amp, npts=1e6, dx_npts=10)

            self.amp = (
                IUS(times - tpeak, amp)(self.times)
                / lalutils.td_amp_scale(mtotal, 1)
                / lal.SpinWeightedSphericalHarmonic(0, 0, -2, 2, 2).real
            )
            self.phase = IUS(times - tpeak, phase)(self.times)
            self.phase -= self.phase[0]
            self.freq = IUS(self.times, self.phase).derivative()(self.times)

            self.h22 = self.amp * np.exp(1.0j * self.phase)
            self.Reh22 = np.real(self.h22)
            self.Imh22 = np.imag(self.h22)


def gen_model_waveforms(approx, qlist, dt, t_min, t_max, nrfiles=None):
    """given a list of mass-ratios, or nrfiles generate the waveforms
    and return a list of instances of `wispy.waveutils.WaveformGeneration`

    Args:
        approx ([type]): [description]
        qlist ([type]): [description]
        dt ([type]): [description]
        t_min ([type]): [description]
        t_max ([type]): [description]
        nrfiles ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    kwargs = dict(dt=dt, t_min=t_min, t_max=t_max)
    if approx == "NR":
        return [WaveformGeneration(nrfile=nrfile, **kwargs) for nrfile in nrfiles]
    else:
        lal_approx = lalsim.GetApproximantFromString(approx)
        return [
            WaveformGeneration(approximant=lal_approx, q=q, **kwargs) for q in qlist
        ]


def taylorT3_leading_term(t, eta, tc):
    """taylorT3 leading term

    Args:
        t ([type]): [description]
        eta ([type]): [description]
        tc ([type]): [description]

    Returns:
        [type]: [description]
    """
    c1 = eta / 5
    td = c1 * (tc - t)
    theta = td ** (-3.0 / 8.0)
    return theta
