import numpy as np

class Sector(object):
    """
    A zone in pyKLIP to reduce the data in. A sector is specified as part of or a whole annulus

    Args: 
        radstart (int): radius the ann
    """

    def __init__(radstart, radend, phistart=None, phiend=None):
        self.radstart = radstart
        self.radend = radend
        if phistart is None:
            self.phistart = 0 
            self.phiend = 2*np
            self.whole_annulus = True
        else:
            self.phistart = phistart
            self.phiend = phiend
            self.whole_annulus = False
        return
       
    def get_sector_indicies(self, img_shape, img_center, padding=0 , IWA=0, OWA=None, parang=None flatten=True, flipx=False):
        pass