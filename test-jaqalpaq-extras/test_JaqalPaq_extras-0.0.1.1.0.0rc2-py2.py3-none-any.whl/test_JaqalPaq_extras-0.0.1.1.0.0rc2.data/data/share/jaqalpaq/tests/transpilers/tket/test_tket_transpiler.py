import unittest, pytest

import jaqalpaq

pytket = pytest.importorskip("pytket")

from jaqalpaq.transpilers.tket import jaqal_circuit_from_tket_circuit
from jaqalpaq.generator import generate_jaqal_program
from numpy import pi
from jaqalpaq.core import CircuitBuilder
from pytket import Circuit


class PytketTranspilerTester(unittest.TestCase):
    def test_transpile_1q_circuit(self):
        c = Circuit(1, 1)
        c.Rz(1, 0)
        c.add_barrier([0])
        c.Measure(0, 0)
        qsc = jaqal_circuit_from_tket_circuit(c)
        jcirc = CircuitBuilder()
        reg = jcirc.register("baseregister", 1)
        reg2 = jcirc.map("q", reg, slice(0, 1, 1))
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Rz", reg2[0], pi)
        block = jcirc.block()
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(qsc)
        )

    def test_transpile_line_circuit(self):
        c = Circuit(2, 2)
        c.Rz(1, 0)
        c.add_barrier([0, 1])
        c.Measure(0, 0)
        c.Measure(1, 1)
        qsc = jaqal_circuit_from_tket_circuit(c)
        jcirc = CircuitBuilder()
        reg = jcirc.register("baseregister", 2)
        reg2 = jcirc.map("q", reg, slice(0, 2, 1))
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Rz", reg2[0], pi)
        block = jcirc.block()
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(qsc)
        )

    def test_transpile_grid_circuit(self):
        c = Circuit()
        qb = pytket._tket.circuit.Qubit("grid", 0, 0)
        c.add_qubit(qb)
        c.Rz(1, qb)
        qsc = jaqal_circuit_from_tket_circuit(c)
        jcirc = CircuitBuilder()
        reg = jcirc.register("baseregister", 1)
        reg2 = jcirc.map("grid0_0", reg, slice(0, 1, 1))
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Rz", reg2[0], pi)
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(qsc)
        )
