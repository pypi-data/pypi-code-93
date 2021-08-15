import sys
import argparse
import logging
from tigerseg import segment
import os
import SimpleITK as sitk
import pkg_resources
import numpy as np


def path(string):
    if os.path.exists(string):
        return string
    else:
        sys.exit(f'File not found: {string}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--i', default='CANDI_HC_001.nii.gz',type=str, help='The name of the input data')
    parser.add_argument('-o', '--o', default="segmentation.nii.gz", type=str, help='The name of the output data')
    parser.add_argument('-model', '--model', default='raw_nu_NKI_freesurfer', type=str, help='The name of the model')
    parser.add_argument("--prediction_dir", default="./predict/freesurfer/OASIS/test")
    parser.add_argument('-permute', '--permute', default='False', type = strtobool, help='enable permute or not')
    args = parser.parse_args()

    input_image = args.i
    segmentation = segment.apply('/NFS/weng/3Dsegmentation/tigerseg')



if __name__ == "__main__":
    print('called as script')
    main()
