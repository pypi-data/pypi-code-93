import unittest, pytest

import jaqalpaq

qiskit = pytest.importorskip("qiskit")

from jaqalpaq.transpilers.qiskit import (
    JaqalMSGate,
    SYGate,
    SYdgGate,
    JaqalRGate,
    ion_pass_manager,
)
from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
from math import pi


class QiskitUnrollerTester(unittest.TestCase):
    def test_stable_gates(self):
        qr = QuantumRegister(2)
        cr = ClassicalRegister(2)
        circ = QuantumCircuit(qr, cr)
        circ.jaqalms(pi / 4, pi / 4, qr[0], qr[1])
        circ.jaqalr(pi / 2, pi / 4, qr[0])
        circ.x(qr[1])
        circ.y(qr[0])
        circ.sx(qr[0])
        circ.sxdg(qr[0])
        circ.sy(qr[1])
        circ.sydg(qr[1])
        circ.measure(qr, cr)
        unrolled = ion_pass_manager().run(circ, output_name=circ.name + " unrolled")
        self.assertEqual(str(circ.draw()), str(unrolled.draw()))
        # We compare the circuit diagrams because comparing the QASM means that we miss circuits that have the same gates re-ordered in a commuting way.

    def test_decompose_h(self):
        qr = QuantumRegister(1)
        circ = QuantumCircuit(qr)
        circ.h(qr[0])
        unrolled = ion_pass_manager().run(circ, output_name=circ.name + " unrolled")
        c2 = QuantumCircuit(qr)
        c2.z(qr[0])
        c2.sy(qr[0])
        self.assertEqual(str(c2.draw()), str(unrolled.draw()))

    def test_decompose_u1(self):
        qr = QuantumRegister(1)
        circ = QuantumCircuit(qr)
        circ.p(pi, qr[0])
        unrolled = ion_pass_manager().run(circ, output_name=circ.name + " unrolled")
        c2 = QuantumCircuit(qr, global_phase=pi / 2)
        c2.rz(pi, qr[0])
        self.assertEqual(str(c2.draw()), str(unrolled.draw()))

    def test_decompose_u3(self):
        qr = QuantumRegister(1)
        circ = QuantumCircuit(qr)
        circ.u(pi, pi / 2, pi / 4, qr[0])
        unrolled = ion_pass_manager().run(circ, output_name=circ.name + " unrolled")
        c2 = QuantumCircuit(qr)
        c2.rz(pi / 4, qr[0])
        c2.jaqalr(pi / 2, pi, qr[0])
        c2.rz(pi / 2, qr[0])
        self.assertEqual(str(c2.draw()), str(unrolled.draw()))

    def test_decompose_cx(self):
        qr = QuantumRegister(2)
        circ = QuantumCircuit(qr)
        circ.cx(qr[0], qr[1])
        unrolled = ion_pass_manager().run(circ, output_name=circ.name + " unrolled")
        c2 = QuantumCircuit(qr)
        c2.sy(qr[0])
        c2.jaqalms(0, pi / 2, qr[0], qr[1])
        c2.sxdg(qr[0])
        c2.sxdg(qr[1])
        c2.sydg(qr[0])
        self.maxDiff = 2000
        self.assertEqual(str(c2.draw()), str(unrolled.draw()))
