import unittest, pytest

import jaqalpaq

qiskit = pytest.importorskip("qiskit")

from jaqalpaq.transpilers.qiskit import (
    get_ion_instance,
)
from qiskit.circuit import QuantumCircuit, QuantumRegister, ClassicalRegister
from math import pi


class QiskitBackendTester(unittest.TestCase):
    def test_bell_pair(self):
        qr = QuantumRegister(2)
        circ = QuantumCircuit(qr)
        circ.jaqalms(pi / 4, pi / 2, qr[0], qr[1])
        instance = get_ion_instance()
        instance.set_config(shots=1024)
        result = instance.execute([circ])
        counts = result.get_counts()
        self.assertEqual(len(counts), 2)
        self.assertTrue("00" in counts)
        self.assertTrue("11" in counts)
