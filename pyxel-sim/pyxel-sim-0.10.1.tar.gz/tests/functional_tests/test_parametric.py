from collections import abc
from pathlib import Path

import pytest

from pyxel.configuration import Configuration, load
from pyxel.detectors import CCD
from pyxel.parametric.parametric import Parametric, ParametricMode
from pyxel.pipelines import DetectionPipeline, Processor

try:
    import pygmo as pg

    WITH_PYGMO = True
except ImportError:
    WITH_PYGMO = False


expected_sequential = [
    (0, [("level", 10), ("initial_energy", 100)]),
    (1, [("level", 20), ("initial_energy", 100)]),
    (2, [("level", 30), ("initial_energy", 100)]),
    (3, [("level", 100), ("initial_energy", 100)]),
    (4, [("level", 100), ("initial_energy", 200)]),
    (5, [("level", 100), ("initial_energy", 300)]),
]

expected_product = [
    (0, [("level", 10), ("initial_energy", 100)]),
    (1, [("level", 10), ("initial_energy", 200)]),
    (2, [("level", 10), ("initial_energy", 300)]),
    (3, [("level", 20), ("initial_energy", 100)]),
    (4, [("level", 20), ("initial_energy", 200)]),
    (5, [("level", 20), ("initial_energy", 300)]),
    (6, [("level", 30), ("initial_energy", 100)]),
    (7, [("level", 30), ("initial_energy", 200)]),
    (8, [("level", 30), ("initial_energy", 300)]),
]


@pytest.mark.skipif(not WITH_PYGMO, reason="Package 'pygmo' is not installed.")
@pytest.mark.parametrize(
    "mode, expected",
    [
        # ('single', expected_single),
        (ParametricMode.Sequential, expected_sequential),
        (ParametricMode.Product, expected_product),
    ],
)
def test_pipeline_parametric_without_init_photon(mode: ParametricMode, expected):
    input_filename = "tests/data/parametric.yaml"
    cfg = load(Path(input_filename))

    assert isinstance(cfg, Configuration)
    assert hasattr(cfg, "parametric")
    assert hasattr(cfg, "ccd_detector")
    assert hasattr(cfg, "pipeline")

    parametric = cfg.parametric
    assert isinstance(parametric, Parametric)

    parametric.parametric_mode = mode

    detector = cfg.ccd_detector
    assert isinstance(detector, CCD)

    assert detector.has_photon is False
    with pytest.raises(
        RuntimeError,
        match=(
            r"Photon array is not initialized ! "
            r"Please use a 'Photon Generation' model"
        ),
    ):
        _ = detector.photon

    pipeline = cfg.pipeline
    assert isinstance(pipeline, DetectionPipeline)

    processor = Processor(detector=detector, pipeline=pipeline)
    result = parametric.debug_parameters(processor)
    assert result == expected

    processor_generator = parametric._processors_it(processor=processor)
    assert isinstance(processor_generator, abc.Generator)

    for proc, _, _ in processor_generator:
        assert isinstance(proc, Processor)

        proc.run_pipeline()
