# import pydicom
# import SimpleITK as sitk
import CIRS_063
import constants as C
from tqdm import tqdm
# import matplotlib.pyplot as plt
import numpy as np
np.seterr(all='ignore')
# import os
# import sitktools
# from Phantom_analysis_toolbox import Phantom_analysis_toolbox as pat
# import math
    

def main():    
    cirs_analysis = CIRS_063.CIRS_063_analyser(dcm_path_list[idx])

    return cirs_analysis.WAD_output
    
    
if __name__ == '__main__':
    dcm_path_list = CIRS_063.dcm_list_builder(C.root_path)
    
    for idx in tqdm(range(len(dcm_path_list))):
        dcm = main()