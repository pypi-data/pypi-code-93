import unittest, pytest

import jaqalpaq

qiskit = pytest.importorskip("qiskit")

from jaqalpaq.transpilers.qiskit import (
    jaqal_circuit_from_qiskit_circuit,
    jaqal_circuit_from_dag_circuit,
)
from jaqalpaq.core import CircuitBuilder
from jaqalpaq.generator import generate_jaqal_program
from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.transpiler import PassManager
from math import pi
from qiskit.converters.circuit_to_dag import circuit_to_dag


class QiskitTranspilerTester(unittest.TestCase):
    def test_transpile_1q_circuit(self):
        qr = QuantumRegister(1)
        cr = ClassicalRegister(2)
        circ = QuantumCircuit(qr, cr)
        circ.x(qr[0])
        circ.measure(qr[0], cr[0])
        circ.barrier(qr[0])
        circ.reset(qr[0])
        circ.y(qr[0])
        circ.measure(qr[0], cr[1])
        jcirc = CircuitBuilder()
        reg1 = jcirc.register("baseregister", 1)
        reg2 = jcirc.map(qr.name, reg1, slice(0, 1, 1))
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Px", reg2[0])
        block.gate("measure_all")
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Py", reg2[0])
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()),
            generate_jaqal_program(jaqal_circuit_from_qiskit_circuit(circ)),
        )

    def test_transpile_2q_circuit(self):
        qr = QuantumRegister(2)
        cr = ClassicalRegister(4)
        circ = QuantumCircuit(qr, cr)
        circ.x(qr[0])
        circ.measure(qr[0], cr[0])
        circ.measure(qr[1], cr[1])
        circ.barrier()
        circ.reset(qr[0])
        circ.reset(qr[1])
        circ.barrier()
        circ.y(qr[0])
        dag = circuit_to_dag(circ)
        jcirc = CircuitBuilder()
        reg1 = jcirc.register("baseregister", 2)
        reg2 = jcirc.map(qr.name, reg1, slice(0, 2, 1))
        block = jcirc.block()
        block.gate("prepare_all")
        block.gate("Px", reg2[0])
        block.gate("measure_all")
        block = jcirc.block()
        block.gate("prepare_all")
        block = jcirc.block()
        block.gate("Py", reg2[0])
        block.gate("measure_all")
        self.assertEqual(
            generate_jaqal_program(jcirc.build()),
            generate_jaqal_program(jaqal_circuit_from_dag_circuit(dag)),
        )
