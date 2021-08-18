import unittest, pytest
import jaqalpaq

pyquil = pytest.importorskip("pyquil")

from pyquil import Program
from pyquil.gates import *
from numpy import pi
from jaqalpaq.transpilers.quil import *
from jaqalpaq.core import CircuitBuilder
from jaqalpaq.generator import generate_jaqal_program


class QuilTranspilerTester(unittest.TestCase):
    def test_1_ion_compilation(self):
        p = Program()
        ro = p.declare("ro", "BIT", 3)
        p += X(0)
        p += MEASURE(0, ro[0])
        p += RESET(0)
        p += X(0)
        p += MEASURE(0, ro[1])
        p += RESET()
        p += X(0)
        p += MEASURE(0, ro[2])
        qc = get_ion_qc(1)
        circ = qc.compile(p)
        jcirc = CircuitBuilder()
        reg = jcirc.register("qreg", 1)
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Px", reg[0])
        block.gate("measure_all")
        block.gate("prepare_all")
        block.gate("Px", reg[0])
        block.gate("measure_all")
        block.gate("prepare_all")
        block.gate("Px", reg[0])
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(circ)
        )

    def test_2_ion_compilation(self):
        p = Program()
        ro = p.declare("ro", "BIT", 6)
        p += X(0)
        p += MEASURE(0, ro[0])
        p += MEASURE(1, ro[1])
        p += RESET(0)
        p += RESET(1)
        p += X(1)
        p += MEASURE(1, ro[3])
        p += MEASURE(0, ro[2])
        p += RESET()
        p += X(0)
        p += MEASURE(0, ro[4])
        p += MEASURE(1, ro[5])
        qc = get_ion_qc(2)
        circ = qc.compile(p)
        jcirc = CircuitBuilder()
        reg = jcirc.register("qreg", 2)
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Px", reg[0])
        block.gate("measure_all")
        block.gate("prepare_all")
        block.gate("Px", reg[1])
        block.gate("measure_all")
        block.gate("prepare_all")
        block.gate("Px", reg[0])
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(circ)
        )

    def test_native_gates(self):
        gates = quil_gates()
        p = Program()
        ro = p.declare("ro", "BIT", 1)
        p += gates["SX"](0)
        p += MEASURE(0, ro[0])
        qc = get_ion_qc(1)
        circ = qc.compile(p)
        jcirc = CircuitBuilder()
        reg = jcirc.register("qreg", 1)
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Sx", reg[0])
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(circ)
        )
