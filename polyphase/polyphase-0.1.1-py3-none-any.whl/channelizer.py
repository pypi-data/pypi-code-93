"""
Channelizer class.
"""

__all__ = ['Channelizer']

import numpy
import scipy.signal
import scipy.fft
import matplotlib.pyplot as plt


class Channelizer(object):
    """
    Channelizer object.
    \param filter_coeffs: Filter coefficient array.
    """

    _channel_num: int
    _filter_coeffs: numpy.ndarray

    def __init__(
            self, 
            filter_coeffs: numpy.ndarray,
            channel_num: int = 8):

        assert  isinstance(channel_num, int)

        self._filter_coeffs = numpy.reshape(filter_coeffs, (channel_num, -1), order='F') 
        self._channel_num = channel_num

    def dispatch(
            self, 
            data: numpy.ndarray
            ) -> numpy.ndarray:

        # Make the data length an integer multiple of the number of channels.
        disp_len = int(numpy.ceil(data.size / self._channel_num))
        patch_size = int(disp_len * self._channel_num - data.size)
        patch_data = numpy.concatenate((data, numpy.zeros(patch_size)))

        # Reshape data.
        reshape_data = numpy.reshape(patch_data, (self._channel_num, -1), order='F')
        polyphase_data = numpy.flipud(reshape_data)

        nv = numpy.arange(disp_len)
        prefilt_data = polyphase_data * ((-1) ** nv)

        # Polyphase filter bank
        filt_data = numpy.zeros(prefilt_data.shape, dtype=complex)
        for k in range(self._channel_num):
            # zi = scipy.signal.lfilter_zi(self._filter_coeffs[k], 1)
            filt_data[k] = scipy.signal.lfilter(self._filter_coeffs[k], 1, prefilt_data[k])

        postfilt_data = numpy.zeros(prefilt_data.shape, dtype=complex)
        for k in range(self._channel_num):
            postfilt_data[k] = filt_data[k] * ((-1) ** k) * numpy.exp(-1j * numpy.pi * k / self._channel_num)

        dispatch_data = scipy.fft.fft(postfilt_data, axis=0)

        return dispatch_data


if __name__ == '__main__':
    channel_num = 128
    # Sampling rate set to 10KHz
    fs = 100000
    # 
    T = 1

    t = numpy.arange(0, int(T*fs)) / fs

    # Generate chirp signal.
    s = scipy.signal.chirp(t, 0, T, fs / 2)

    # s = numpy.ones(400)
    # s = numpy.exp((0.5/N*t)*2j*numpy.pi*t)

    # 
    cutoff = fs / channel_num / 2    # Desired cutoff frequency, Hz
    trans_width = cutoff / 2  # Width of transition from pass band to stop band, Hz
    numtaps = 512      # Size of the FIR filter.
    taps = scipy.signal.remez(numtaps, [0, cutoff - trans_width, cutoff + trans_width, 0.5*fs],
                        [1, 0], Hz=fs)
    
    
    # taps = [0.000302, 0.000038, -0.000169, -0.000406, -0.000481, -0.000255, 0.000234, 0.000728, 0.000866, 0.000425, -0.000473, -0.001334, -0.001535, -0.000739, 0.000790, 0.002200, 0.002492, 0.001175, -0.001262, -0.003450, -0.003858, -0.001796, 0.001924, 0.005199, 0.005763, 0.002657, -0.002850, -0.007642, -0.008428, -0.003866, 0.004159, 0.011116, 0.012250, 0.005616, -0.006088, -0.016318, -0.018088, -0.008353, 0.009203, 0.025008, 0.028259, 0.013368, -0.015287, -0.043323, -0.051877, -0.026574, 0.034320, 0.116868, 0.195631, 0.243618, 0.243618, 0.195631, 0.116868, 0.034320, -0.026574, -0.051877, -0.043323, -0.015287, 0.013368, 0.028259, 0.025008, 0.009203, -0.008353, -0.018088, -0.016318, -0.006088, 0.005616, 0.012250, 0.011116, 0.004159, -0.003866, -0.008428, -0.007642, -0.002850, 0.002657, 0.005763, 0.005199, 0.001924, -0.001796, -0.003858, -0.003450, -0.001262, 0.001175, 0.002492, 0.002200, 0.000790, -0.000739, -0.001535, -0.001334, -0.000473, 0.000425, 0.000866, 0.000728, 0.000234, -0.000255, -0.000481, -0.000406, -0.000169, 0.000038, 0.000302]
    
    w, h = scipy.signal.freqz(taps)
    
    plt.subplot(221)
    plt.plot(taps)
    
    plt.subplot(222)
    plt.plot(w, 20 * numpy.log10(abs(h)), 'b')
    

    channelizer = Channelizer(taps, channel_num)

    ss_abs = 20*numpy.log10(numpy.abs(channelizer.dispatch(s)))

    plt.subplot(223)
    plt.plot(numpy.real(s))
    plt.subplot(224)
    plt.plot(ss_abs.T)
    plt.show()
    











