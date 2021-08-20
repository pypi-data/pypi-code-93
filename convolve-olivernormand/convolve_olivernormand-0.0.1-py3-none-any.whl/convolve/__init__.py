import numpy as np

def correlate(signal, kernel):
    M = signal.shape[0] - kernel.shape[0] + 1
    m = kernel.shape[0]
    output = np.empty(M)
    for i in range(M):
        output[i] = np.sum(kernel * signal[i:i + m])
        print(i)
    return output

def convert_to_windows(signal, kernel_shape):
    """
        For a given input signal, will convert to a 4D numpy array with shape
            output.shape = (n_y, n_x, kernel_shape[0], kernel_shape[1])
        This allows subsequent multiplication of each window by the kernel to generate the output convolution
    """
    m0, n0 = signal.shape
    m1, n1 = kernel_shape
    output_shape = (m0 - m1 + 1, n0 - n1 + 1)

    # output_shape must be positive
    if output_shape[0] <= 0 or output_shape[1] <= 0:
        print("Error: output_shape must be positive")
        return None

    output_array = np.zeros([output_shape[0], output_shape[1], m1, n1])

    for i in range(output_shape[0]):
        for j in range(output_shape[1]):
            output_array[i, j, :, :] = signal[i: i + m1, j: j + n1]

    return output_array

def correlate2D(signal, kernel, padding = None):

    if padding:
        npad = (kernel.shape[0] - 1, kernel.shape[1] - 1)
        if isintance(padding, str):
            signal = np.pad(signal, npad, mode = padding)
        else:
            signal = np.pad(signal, npad, mode = 'constant', constant_values = padding)

    windows = convert_to_windows(signal, kernel.shape)
    kernel = kernel[np.newaxis, np.newaxis, :, :]

    """
        windows has shape (m, n, kernel_m, kernel_n) and hence when multiplied with
        the kernel will multiply each window individually. We then go across and sum the axes.
    """

    output = np.sum(np.sum(windows * kernel, axis = -1), -1)
    return output

def convolve2D(signal, kernel, padding = None):
    # Convolution operation equivalent to correlation with flipped kernel
    return correlate2D(signal, kernel[::-1, ::-1], padding)
