
import os.path
import numpy as np
from skimage import io


def mean_std(input_files, mean_file='mean', std_file='std'):
    if not input_files:
        raise ValueError('no input image files defined')
    if not os.path.splitext(mean_file)[1]:
        _, ext    = os.path.splitext(input_files[0])
        mean_file = '.'.join((mean_file, ext))
        std_file  = '.'.join((std_file,  ext))
    m0 = len(input_files)
    m1 = m2 = None
    for input_file in input_files:
        img = io.imread(input_file)
        if m1 is None:
            m1 = np.sum(img, axis=2)
            m2 = np.sum(img*img, axis=2)
        else:
            m1 += np.sum(img, axis=2)
            m2 += np.sum(img*img, axis=2)
    mean = m1 / m0
    std = np.sqrt( m2/m0 - mean*mean )
    io.imsave(mean_file, mean)
    io.imsave(std_file, std)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', help='paths to raw image files')
    parser.add_argument('-m', '--mean', default='mean.tif', help='mean image output file')
    parser.add_argument('-s', '--std', default='std.tif', help='standard deviation image output file')
    args = parser.parse_args()

    assert isinstance(args.files, list)
    assert isinstance(args.mean, str)
    assert isinstance(args.std, str)
    mean_std(args.files, args.mean, args.std)


if __name__ == '__main__':
    main()

