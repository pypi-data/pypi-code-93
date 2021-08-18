import unittest, pytest

import jaqalpaq

projectq = pytest.importorskip("projectq")

import projectq
from projectq.cengines import MainEngine, DummyEngine
from projectq.ops import SqrtX, H, CNOT, Rz, Measure, Rx, Ry, Rxx, Ryy, All, Barrier
from jaqalpaq.transpilers.projectq import get_engine_list, JaqalBackend
from jaqalpaq.generator import generate_jaqal_program
from math import pi
from jaqalpaq.core import CircuitBuilder


class ProjectQTranspilerTester(unittest.TestCase):
    def test_transpile_circuit(self):
        backend = JaqalBackend()
        engine_list = get_engine_list()
        eng = MainEngine(backend, engine_list, verbose=True)
        q1 = eng.allocate_qubit()
        q2 = eng.allocate_qubit()
        SqrtX | q1
        SqrtX | q2
        Barrier | (q1, q2)
        Rxx(1.0) | (q1, q2)
        All(Measure) | [q1, q2]
        eng.flush()
        circ = backend.circuit
        jcirc = CircuitBuilder()
        reg = jcirc.register("q", 2)
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Sx", reg[0])
        block.gate("Sx", reg[1])
        block = jcirc.block()
        block.gate("MS", reg[0], reg[1], 0, 1.0)
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(circ)
        )
