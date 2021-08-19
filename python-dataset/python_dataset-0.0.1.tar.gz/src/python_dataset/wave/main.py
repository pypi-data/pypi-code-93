import math
import numpy as np

from pathlib import Path
from typing import Tuple

import pyworld as pw
import pysptk as ps
import librosa

from ..property import define_property, define_properties


class WaveInfo(object):

    Vector = "np.ndarray[np.float64]"

    wave_name: str = None
    person_name: str = None
    path: Path = None

    @define_properties(readable=("path"), accessible=("wave_name", "person_name"))
    def __init__(
        self,
        wave_name: str = wave_name,
        person_name: str = person_name,
        path: Path = path,
    ) -> None:
        pass


class SampledWave(object):

    Vector = "np.ndarray[np.float64]"

    ampl: Vector = None
    fs: int = None

    @define_properties(readable=("fs"), accessible=("ampl"))
    def __init__(
        self,
        ampl: Vector = ampl,
        fs: int = fs,
    ) -> None:
        pass

    def load_wav(
        self,
        fs: int = fs,
        path: Path = None,
        dtype: "np.dtype" = np.float64,
        top_db: int = 40,
    ) -> Tuple[Vector, int]:
        ampl, fs = librosa.load(path, fs, dtype=dtype)
        ampl = librosa.effects.remix(
            ampl, intervals=librosa.effects.split(ampl, top_db=50)
        )
        tmp = len(ampl) % 4
        if tmp:
            ampl = ampl[:-tmp]
        return ampl, fs


class Features(object):

    Vector = "np.ndarray[np.float64]"

    f0: Vector = None
    sp: Vector = None
    ap: Vector = None

    mc: Vector = None
    mfcc: Vector = None

    @define_properties
    def __init__(
        self,
        f0: Vector = f0,
        sp: Vector = sp,
        ap: Vector = ap,
        mc: Vector = mc,
        mfcc: Vector = mfcc,
    ) -> None:
        pass

    def extract_base(
        self,
        ampl: Vector = None,
        fs: int = None,
    ) -> Tuple[Vector, Vector, Vector]:
        return pw.wav2world(ampl, fs)

    def extract_mc(
        self,
        sp: Vector = sp,
        order: int = 35,
        fs: int = 22050,
        alpha: float = 0.46,
    ) -> Vector:
        mc = ps.conversion.sp2mc(powerspec=sp, order=order, alpha=alpha)
        return mc

    def extract_mfcc(
        self, ampl: Vector = None, fs: int = 22050, order: int = 36
    ) -> Vector:
        return librosa.feature.mfcc(ampl, fs, n_mfcc=order)

    def extract_sp(self):
        pass


class Wave(WaveInfo, SampledWave, Features):

    Vector = "np.ndarray[np.float64]"

    wave_name: str = None
    person_name: str = None
    path: Path

    fs: int = 22050
    order: int = 36

    ex_base: bool = True
    ex_mc: bool = False
    ex_mfcc: bool = False

    def __init__(
        self,
        path: Path,
        data_path: Path,
        wave_name: str = None,
        person_name: str = None,
        fs: int = fs,
        order: int = order,
        ex_base: bool = ex_base,
        ex_mc: bool = ex_mc,
        ex_mfcc: bool = ex_mfcc,
    ) -> None:

        WaveInfo.__init__(
            self,
            wave_name=wave_name,
            person_name=person_name,
            path=path,
        )

        ampl, fs = self.load_wav(data_path / path, fs)
        SampledWave.__init__(self, ampl=ampl, fs=fs)
        Features.__init__(self)

        if ex_base:
            self.extract_base()

        if ex_mc:
            self.extract_mc()

        if ex_mfcc:
            self.extract_mfcc()

    def load_wav(self, path, fs) -> Tuple[Vector, int]:
        return super().load_wav(path=path, fs=fs)

    def extract_base(self) -> None:
        f0, sp, ap = super().extract_base(self.ampl, self.fs)
        tmp = len(f0) % 4
        if tmp:
            f0 = f0[:-tmp]
            sp = sp[:-tmp]
            ap = ap[:-tmp]
        self.f0, self.sp, self.ap = f0, sp, ap

    def extract_mc(self) -> None:
        self.mc = super().extract_mc(self.sp, self.order - 1, self.fs)

    def extract_mfcc(self) -> None:
        self.mfcc = super().extract_mfcc(self.ampl, self.fs, self.order)
