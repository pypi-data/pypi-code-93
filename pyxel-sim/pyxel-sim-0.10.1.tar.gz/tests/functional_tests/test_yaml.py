#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

import pytest

from pyxel import inputs_outputs as io

try:
    import pygmo as pg

    WITH_PYGMO = True
except ImportError:
    WITH_PYGMO = False

from pyxel.calibration import Algorithm, Calibration, CalibrationMode
from pyxel.configuration import Configuration, load
from pyxel.data_structure import Charge, Image, Pixel, Signal
from pyxel.detectors import CCD, CCDCharacteristics, CCDGeometry, Environment, Material
from pyxel.dynamic import Dynamic
from pyxel.inputs_outputs.calibration_outputs import CalibrationOutputs
from pyxel.inputs_outputs.dynamic_outputs import DynamicOutputs
from pyxel.inputs_outputs.parametric_outputs import ParametricOutputs
from pyxel.inputs_outputs.single_outputs import SingleOutputs
from pyxel.parametric import Parametric, ParametricMode
from pyxel.pipelines import DetectionPipeline, ModelFunction, ModelGroup
from pyxel.single import Single


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "yaml_file",
    [
        "tests/data/parametric.yaml",
        "tests/data/yaml.yaml",
        "tests/data/calibrate_models.yaml",
    ],
)
def test_yaml_load(yaml_file):
    cfg = load(yaml_file)

    assert isinstance(cfg, Configuration)

    if isinstance(cfg.single, Single):
        assert isinstance(cfg.single.outputs, SingleOutputs)
    elif isinstance(cfg.calibration, Calibration):
        assert isinstance(cfg.calibration.outputs, CalibrationOutputs)
        assert isinstance(cfg.calibration.algorithm, Algorithm)
        assert isinstance(cfg.calibration.calibration_mode, CalibrationMode)
    elif isinstance(cfg.dynamic, Dynamic):
        assert isinstance(cfg.dynamic.outputs, DynamicOutputs)
    elif isinstance(cfg.parametric, Parametric):
        assert isinstance(cfg.parametric.outputs, ParametricOutputs)
        assert isinstance(cfg.parametric.parametric_mode, ParametricMode)
    else:
        raise AssertionError("Running mode not initialized.")

    assert isinstance(cfg.ccd_detector, CCD)
    assert isinstance(cfg.ccd_detector.geometry, CCDGeometry)
    assert isinstance(cfg.ccd_detector.characteristics, CCDCharacteristics)
    assert isinstance(cfg.ccd_detector.material, Material)
    assert isinstance(cfg.ccd_detector.environment, Environment)
    assert isinstance(cfg.ccd_detector.image, Image)
    assert isinstance(cfg.ccd_detector.signal, Signal)
    assert isinstance(cfg.ccd_detector.pixel, Pixel)
    assert isinstance(cfg.ccd_detector.charge, Charge)

    assert isinstance(cfg.pipeline, DetectionPipeline)
    assert isinstance(cfg.pipeline.photon_generation, ModelGroup)
    assert isinstance(cfg.pipeline.photon_generation.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_generation, ModelGroup)
    assert isinstance(cfg.pipeline.charge_generation.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_collection, ModelGroup)
    assert isinstance(cfg.pipeline.charge_collection.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_transfer, ModelGroup)
    assert isinstance(cfg.pipeline.charge_transfer.models[0], ModelFunction)
    assert isinstance(cfg.pipeline.charge_measurement, ModelGroup)
    assert isinstance(cfg.pipeline.charge_measurement.models[0], ModelFunction)
