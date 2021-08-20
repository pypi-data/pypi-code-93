import numpy as np
import scipy.signal

def compute_time(mag, fs):
    return np.arange(0, len(mag))/fs

def calc_fft(mag, fs):

    fmag = np.abs(np.fft.fft(mag))
    f = np.linspace(0, fs // 2, len(mag) // 2)

    return f[:len(mag) // 2].copy(), fmag[:len(mag) // 2].copy()

def wavelet(mag, function=scipy.signal.ricker, widths=np.arange(1, 10)):

    if isinstance(function, str):
        function = eval(function)

    if isinstance(widths, str):
        widths = eval(widths)

    cwt = scipy.signal.cwt(mag, function, widths)

    return cwt