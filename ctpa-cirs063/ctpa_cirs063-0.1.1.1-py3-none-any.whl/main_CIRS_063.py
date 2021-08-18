from cirs_063 import CIRS_063
import constants as C
from tqdm import tqdm
import numpy as np
np.seterr(all='ignore')
    

def main():    
    cirs_analysis = CIRS_063.CIRS_063_analyser(dcm_path_list[idx])

    return cirs_analysis.WAD_output
    
    
if __name__ == '__main__':
    dcm_path_list = CIRS_063.dcm_list_builder(C.root_path)
    
    for idx in tqdm(range(len(dcm_path_list))):
        dcm = main()