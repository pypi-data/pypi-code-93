import numpy as np
import math


class HMUtil:
    def convert_xyzabc_to_hm(func):
        def wrapper(*args, **kwargs):
            funcout = func(*args, **kwargs)
            [x, y, z, a, b, c] = funcout

            ca = math.cos(a)
            sa = math.sin(a)
            cb = math.cos(b)
            sb = math.sin(b)
            cc = math.cos(c)
            sc = math.sin(c)
            H = np.array(
                [
                    [cb * cc, cc * sa * sb - ca * sc, sa * sc + ca * cc * sb, x],
                    [cb * sc, ca * cc + sa * sb * sc, ca * sb * sc - cc * sa, y],
                    [-sb, cb * sa, ca * cb, z],
                    [0, 0, 0, 1],
                ]
            )
            return H

        return wrapper

    def convert_hm_to_xyzabc(func):
        def wrapper(*args, **kwargs):
            H = args[0]
            x = H[0, 3]
            y = H[1, 3]
            z = H[2, 3]
            if H[2, 0] > (1.0 - 1e-10):
                b = -math.pi / 2
                a = 0
                c = math.atan2(-H[1, 2], H[1, 1])
            elif H[2, 0] < -1.0 + 1e-10:
                b = math.pi / 2
                a = 0
                c = math.atan2(H[1, 2], H[1, 1])
            else:
                b = math.atan2(
                    -H[2, 0], math.sqrt(H[0, 0] * H[0, 0] + H[1, 0] * H[1, 0])
                )
                c = math.atan2(H[1, 0], H[0, 0])
                a = math.atan2(H[2, 1], H[2, 2])
            funcout = func([x, y, z, a, b, c])
            return funcout

        return wrapper

    @staticmethod
    @convert_xyzabc_to_hm
    def convert_xyzabc_to_hm_by_deg(xyzabc):
        [x, y, z, a, b, c] = xyzabc
        a = a * math.pi / 180
        b = b * math.pi / 180
        c = c * math.pi / 180
        return [x, y, z, a, b, c]

    @staticmethod
    @convert_xyzabc_to_hm
    def convert_xyzabc_to_hm_by_rad(xyzabc):
        return xyzabc

    @staticmethod
    @convert_hm_to_xyzabc
    def convert_hm_to_xyzabc_by_deg(xyzabc):
        [x, y, z, a, b, c] = xyzabc
        return [x, y, z, a * 180 / math.pi, b * 180 / math.pi, c * 180 / math.pi]

    """
    HM =        R(3x3)     d(3x1)
                0(1x3)     1(1x1)

    HMInv =     R.T(3x3)   -R.T(3x3)*d(3x1)
                0(1x3)     1(1x1)

                (R^-1 = R.T)
    """

    @staticmethod
    def inverse_homogeneous_matrix(H):
        rot = H[0:3, 0:3]
        trs = H[0:3, 3]

        HMInv = np.zeros([4, 4], dtype=np.float64)
        HMInv[0:3, 0:3] = rot.T
        HMInv[0:3, 3] = (-1.0) * np.dot(rot.T, trs)
        HMInv[3, 0:4] = [0.0, 0.0, 0.0, 1.0]
        return HMInv

    @staticmethod
    def create_homogeneous_matrix(rot, trans):
        HM = np.zeros([4, 4], dtype=np.float64)
        HM[0:3, 0:3] = rot
        HM[0:3, 3] = trans
        HM[3, 0:4] = [0.0, 0.0, 0.0, 1.0]
        return HM

