import numpy as np

from .rim import Rim
from .hub import Hub


class Wheel(object):
    def __init__(self, hub=None, rim=None, cross_l=3, cross_r=3, spoke=2.0):
        self.hub = hub if hub else Hub()
        self.rim = rim if rim else Rim()
        self.cross_l = cross_l
        self.cross_r = cross_r
        self.spoke = spoke

    def __repr__(self):
        return str(self.__dict__)

    def vec_lr(self):
        """this vector pair is calculated based on
        vec( center to hub hole ) + vec( spoke ) = vec( center to rim )
        where vec( spoke ) is wanted"""

        rim = self.rim.vec()

        hub_l = self.hub.left.vec(self.cross_l)
        hub_r = self.hub.right.vec(self.cross_r)

        return (rim - hub_l, rim - hub_r)

    def spoke_lr(self, decimals=0):
        l, r = self.vec_lr()

        norm_l = np.linalg.norm(l)
        norm_r = np.linalg.norm(r)

        len_l = np.round(norm_l, decimals)
        len_r = np.round(norm_r, decimals)

        # todo ?
        # remove minimal calc errors below

        # the spoke head itself moves towards the spoke nipple (when setting)
        # and therefore out of the theorectical center of the flange
        # the spoke effective length can be recuded by
        # half of the difference between spoke hole and thickness
        rel_l = (
            (self.hub.left.spoke_hole - self.spoke) / 2.0
            if self.hub.left.spoke_hole != None
            else 0
        )
        rel_r = (
            (self.hub.right.spoke_hole - self.spoke) / 2.0
            if self.hub.right.spoke_hole != None
            else 0
        )

        # todo
        # the spoke of each flange adds, or reduces the real flange distance
        # by half of flange thickness and half of spoke thickness
        # depending on their spoke position (outside, or inside head position)
        # what might be around +/-1mm (as assumnption)
        # take a shorter spoke since nipple might be long enough ?!

        return (len_l - rel_l, len_r - rel_r)
