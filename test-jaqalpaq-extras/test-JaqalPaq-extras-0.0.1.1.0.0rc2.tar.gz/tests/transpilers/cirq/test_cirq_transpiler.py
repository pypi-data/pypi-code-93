import unittest, pytest

import jaqalpaq

cirq = pytest.importorskip("cirq")

from jaqalpaq.transpilers.cirq import jaqal_circuit_from_cirq_circuit
from jaqalpaq.generator import generate_jaqal_program
from math import pi
from jaqalpaq.core import CircuitBuilder


class CirqTranspilerTester(unittest.TestCase):
    def test_transpile_line_circuit(self):
        c = cirq.Circuit()
        qubits = [cirq.LineQubit(0), cirq.LineQubit(1)]
        c.append(cirq.H.on(qubits[0]))
        c.append(cirq.CNOT(*qubits))
        ic = cirq.ConvertToIonGates().convert_circuit(c)
        ic.append(
            cirq.measure_each(*qubits),
            strategy=cirq.circuits.InsertStrategy.NEW_THEN_INLINE,
        )
        jc = jaqal_circuit_from_cirq_circuit(ic)
        jcirc = CircuitBuilder()
        reg = jcirc.register("allqubits", 2)
        jcirc.gate("prepare_all")
        jcirc.gate("R", reg[0], pi, pi)
        jcirc.gate("MS", reg[0], reg[1], 0, pi / 2)
        block = jcirc.block(True)
        block.gate("R", reg[0], -1.5707963267948972, pi / 2)
        # Last few digits are off if we just use -pi/2
        block.gate("R", reg[1], pi, pi / 2)
        jcirc.gate("Rz", reg[0], -pi / 2)
        jcirc.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()), generate_jaqal_program(jc)
        )
