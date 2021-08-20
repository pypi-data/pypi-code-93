import numpy as np
import scipy.signal
from gatspy.periodic import LombScargleFast
from astropy.timeseries import LombScargle
from features.utils import *

fs=100

def period(time,mag):
    gatspy_period = LombScargleFast()
    gatspy_period.fit(time, mag, 0.01)
    gatspy_period.optimizer.period_range=(0.1, 10)
    originalPeriod = gatspy_period.best_period
    return originalPeriod

def falseProbAlarm(time, mag):
        ls = LombScargle(time, mag, 1.0)
        freq, power = ls.autopower()
        return ls.false_alarm_probability(power.max())
    
def rcs(mag): 
        sigma = np.std(mag)
        N = len(mag)
        m = np.mean(mag)
        s = np.cumsum(mag - m) * 1.0 / (N * sigma)
        R = np.max(s) - np.min(s)
        return R
        
def stetsonK(mag):
        error = np.random.normal(loc=0.035, scale=0.005, size=mag.shape[0])
        
        mean_mag = (np.sum(mag/(error*error)) /
                        np.sum(1.0 / (error * error)))
        
        N = len(mag)
        sigmap = (np.sqrt(N * 1.0 / (N - 1)) *
                  (mag - mean_mag) / error)

        K = (1 / np.sqrt(N * 1.0) *
             np.sum(np.abs(sigmap)) / np.sqrt(np.sum(sigmap ** 2)))

        return K    

def autocorr(mag):
    return float(np.correlate(mag, mag))

def calc_centroid(mag, fs):
    time = compute_time(mag, fs)

    energy = np.array(mag) ** 2

    t_energy = np.dot(np.array(time), np.array(energy))
    energy_sum = np.sum(energy)

    if energy_sum == 0 or t_energy == 0:
        centroid = 0
    else:
        centroid = t_energy / energy_sum

    return centroid

def mean_abs_diff(mag):
    return np.mean(np.abs(np.diff(mag)))

def mean_diff(mag):
    return np.mean(np.diff(mag))

def median_abs_diff(mag):
    return np.median(np.abs(np.diff(mag)))

def median_diff(mag):
    return np.median(np.diff(mag))

def distance(mag):
    diff_sig = np.diff(mag).astype(float)
    return np.sum([np.sqrt(1 + diff_sig ** 2)])

def sum_abs_diff(mag):
    return np.sum(np.abs(np.diff(mag)))

def slope(mag):
    t = np.linspace(0, len(mag) - 1, len(mag))

    return np.polyfit(t, mag, 1)[0]

def auc(mag, fs):
    t = compute_time(mag, fs)

    return np.sum(0.5 * np.diff(t) * np.abs(np.array(mag[:-1]) + np.array(mag[1:])))

def pk_pk_distance(mag):
    return np.abs(np.max(mag) - np.min(mag))

def entropy(mag, prob='standard'):
    if prob == 'standard':
        value, counts = np.unique(mag, return_counts=True)
        p = counts / counts.sum()
    elif prob == 'kde':
        p = kde(mag)
    elif prob == 'gauss':
        p = gaussian(mag)

    if np.sum(p) == 0:
        return 0.0

    p = p[np.where(p != 0)]

    if np.log2(len(mag)) == 1:
        return 0.0
    elif np.sum(p * np.log2(p)) / np.log2(len(mag)) == 0:
        return 0.0
    else:
        return - np.sum(p * np.log2(p)) / np.log2(len(mag))

def neighbourhood_peaks(mag, n=10):
    mag = np.array(mag)
    subsequence = mag[n:-n]
    peaks = ((subsequence > np.roll(mag, 1)[n:-n]) & (subsequence > np.roll(mag, -1)[n:-n]))
    for i in range(2, n + 1):
        peaks &= (subsequence > np.roll(mag, i)[n:-n])
        peaks &= (subsequence > np.roll(mag, -i)[n:-n])
    return np.sum(peaks)

def hist(mag, nbins=10, r=1):
    histsig, bin_edges = np.histogram(mag, bins=nbins, range=[-r, r]) 

    return tuple(histsig)

def interq_range(mag):
    return np.percentile(mag, 75) - np.percentile(mag, 25)

def kurtosis(mag):
    return scipy.stats.kurtosis(mag)

def skewness(mag):
    return scipy.stats.skew(mag)

def calc_max(mag):
    return np.max(mag)

def calc_min(mag):
    return np.min(mag)

def calc_mean(mag):
    return np.mean(mag)

def calc_median(mag):
    return np.median(mag)

def mean_abs_deviation(mag):
    return np.mean(np.abs(mag - np.mean(mag, axis=0)), axis=0)

def median_abs_deviation(mag):
    return scipy.stats.median_absolute_deviation(mag, scale=1)

def rms(mag):
    return np.sqrt(np.sum(np.array(mag) ** 2) / len(mag))

def calc_std(mag):
    return np.std(mag)

def calc_var(mag):
    return np.var(mag)

def ecdf(mag, d=10):
    y =  np.arange(1, len(mag)+1)/len(mag)
    if len(mag) <= d:
        return tuple(y)
    else:
        return tuple(y[:d])

def spectral_distance(mag, fs):
    f, fmag = calc_fft(mag, fs)

    cum_fmag = np.cumsum(fmag)

    points_y = np.linspace(0, cum_fmag[-1], len(cum_fmag))

    return np.sum(points_y - cum_fmag)

def fundamental_frequency(mag, fs):
    mag = mag - np.mean(mag)
    f, fmag = calc_fft(mag, fs)

    bp = scipy.signal.find_peaks(fmag, height=max(fmag) * 0.3)[0]

    bp = bp[bp != 0]
    if not list(bp):
        f0 = 0
    else:
        f0 = f[min(bp)]

    return f0

def max_power_spectrum(mag, fs):
    if np.std(mag) == 0:
        return float(max(scipy.signal.welch(mag, int(fs), nperseg=len(mag))[1]))
    else:
        return float(max(scipy.signal.welch(mag / np.std(mag), int(fs), nperseg=len(mag))[1]))

def max_frequency(mag, fs):
    f, fmag = calc_fft(mag, fs)
    cum_fmag = np.cumsum(fmag)

    try:
        ind_mag = np.where(cum_fmag > cum_fmag[-1] * 0.95)[0][0]
    except IndexError:
        ind_mag = np.argmax(cum_fmag)

    return f[ind_mag]

def median_frequency(mag, fs):
    f, fmag = calc_fft(mag, fs)
    cum_fmag = np.cumsum(fmag)
    try:
        ind_mag = np.where(cum_fmag > cum_fmag[-1] * 0.50)[0][0]
    except IndexError:
        ind_mag = np.argmax(cum_fmag)
    f_median = f[ind_mag]

    return f_median

def spectral_centroid(mag, fs):
    f, fmag = calc_fft(mag, fs)
    if not np.sum(fmag):
        return 0
    else:
        return np.dot(f, fmag / np.sum(fmag))

def spectral_decrease(mag, fs):
    f, fmag = calc_fft(mag, fs)

    fmag_band = fmag[1:]
    len_fmag_band = np.arange(2, len(fmag) + 1)

    soma_num = np.sum((fmag_band - fmag[0]) / (len_fmag_band - 1), axis=0)

    if not np.sum(fmag_band):
        return 0
    else:
        soma_den = 1 / np.sum(fmag_band)
        return soma_den * soma_num

def spectral_kurtosis(mag, fs):
    f, fmag = calc_fft(mag, fs)
    if not spectral_spread(mag, fs):
        return 0
    else:
        spect_kurt = ((f - spectral_centroid(mag, fs)) ** 4) * (fmag / np.sum(fmag))
        return np.sum(spect_kurt) / (spectral_spread(mag, fs) ** 4)

def spectral_skewness(mag, fs):
    f, fmag = calc_fft(mag, fs)
    spect_centr = spectral_centroid(mag, fs)

    if not spectral_spread(mag, fs):
        return 0
    else:
        skew = ((f - spect_centr) ** 3) * (fmag / np.sum(fmag))
        return np.sum(skew) / (spectral_spread(mag, fs) ** 3)

def spectral_spread(mag, fs):
    f, fmag = calc_fft(mag, fs)
    spect_centroid = spectral_centroid(mag, fs)

    if not np.sum(fmag):
        return 0
    else:
        return np.dot(((f - spect_centroid) ** 2), (fmag / np.sum(fmag))) ** 0.5

def spectral_slope(mag, fs):
    f, fmag = calc_fft(mag, fs)
    sum_fmag = fmag.sum()
    dot_ff = (f * f).sum()
    sum_f = f.sum()
    len_f = len(f)

    if not ([f]) or (sum_fmag == 0):
        return 0
    else:
        if not (len_f * dot_ff - sum_f ** 2):
            return 0
        else:
            num_ = (1 / sum_fmag) * (len_f * np.sum(f * fmag) - sum_f * sum_fmag)
            denom_ = (len_f * dot_ff - sum_f ** 2)
            return num_ / denom_

def spectral_variation(mag, fs):
    f, fmag = calc_fft(mag, fs)

    sum1 = np.sum(np.array(fmag)[:-1] * np.array(fmag)[1:])
    sum2 = np.sum(np.array(fmag)[1:] ** 2)
    sum3 = np.sum(np.array(fmag)[:-1] ** 2)

    if not sum2 or not sum3:
        variation = 1
    else:
        variation = 1 - (sum1 / ((sum2 ** 0.5) * (sum3 ** 0.5)))

    return variation

def power_bandwidth(mag, fs):
    if np.std(mag) == 0:
        freq, power = scipy.signal.welch(mag, fs, nperseg=len(mag))
    else:
        freq, power = scipy.signal.welch(mag / np.std(mag), fs, nperseg=len(mag))

    if np.sum(power) == 0:
        return 0.0

    cum_power = np.cumsum(power)
    f_lower = freq[np.where(cum_power >= cum_power[-1] * 0.95)[0][0]]

    cum_power_inv = np.cumsum(power[::-1])
    f_upper = freq[np.abs(np.where(cum_power_inv >= cum_power[-1] * 0.95)[0][0] - len(power) + 1)]

    return np.abs(f_upper - f_lower)

def fft_mean_coeff(mag, fs, nfreq=256):
    if nfreq > len(mag) // 2 + 1:
        nfreq = len(mag) // 2 + 1

    fmag_mean = scipy.signal.spectrogram(mag, fs, nperseg=nfreq * 2 - 2)[2].mean(1)

    return tuple(fmag_mean)

def spectral_entropy(mag, fs):
    sig = mag - np.mean(mag)

    f, fmag = calc_fft(sig, fs)

    power = fmag ** 2

    if power.sum() == 0:
        return 0.0

    prob = np.divide(power, power.sum())

    prob = prob[prob != 0]

    if prob.size == 1:
        return 0.0

    return -np.multiply(prob, np.log2(prob)).sum() / np.log2(prob.size)

def wavelet_entropy(mag, function=scipy.signal.ricker, widths=np.arange(1, 10)):
    if np.sum(mag) == 0:
        return 0.0

    cwt = wavelet(mag, function, widths)
    energy_scale = np.sum(np.abs(cwt), axis=1)
    t_energy = np.sum(energy_scale)
    prob = energy_scale / t_energy
    w_entropy = -np.sum(prob * np.log(prob))

    return w_entropy

def wavelet_abs_mean(mag, function=scipy.signal.ricker, widths=np.arange(1, 10)):
    return tuple(np.abs(np.mean(wavelet(mag, function, widths), axis=1)))

def wavelet_std(mag, function=scipy.signal.ricker, widths=np.arange(1, 10)):
    return tuple((np.std(wavelet(mag, function, widths), axis=1)))

def wavelet_var(mag, function=scipy.signal.ricker, widths=np.arange(1, 10)):
    return tuple((np.var(wavelet(mag, function, widths), axis=1)))

def wavelet_energy(mag, function=scipy.signal.ricker, widths=np.arange(1, 10)):
    cwt = wavelet(mag, function, widths)
    energy = np.sqrt(np.sum(cwt ** 2, axis=1) / np.shape(cwt)[1])

    return tuple(energy)
