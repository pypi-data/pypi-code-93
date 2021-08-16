from qiskit.result.result import Result
from qiskit.providers.basejob import BaseJob
from qiskit.providers.basebackend import BaseBackend
from qiskit.providers.jobstatus import JobStatus
from qiskit import Aer
from qiskit.utils import QuantumInstance
from .frontend import jaqal_circuit_from_qiskit_circuit, ion_pass_manager
from qiskit.transpiler import PassManager
from jaqalpaq.emulator import run_jaqal_circuit
import numpy as np
from collections import Counter


class IonResult:
    def __init__(self, counts):
        self.counts = counts

    def get_counts(self, name=None):
        if len(self.counts) == 1:
            return next(iter(self.counts.values()))
        if isinstance(name, int):
            name = list(self.counts.keys())[name]
        return self.counts[name]

    def data(self, idx):
        return {}


class IonInstance(QuantumInstance):
    def __init__(
        self,
        backend,
        names=None,
        native_gates=None,
        param_maps=None,
        jaqal_backend=None,
        **kwargs,
    ):
        super().__init__(backend, **kwargs)
        self.transpiler_args = {
            "names": names,
            "native_gates": native_gates,
            "param_maps": param_maps,
        }

    def transpile(self, circuits):
        if isinstance(circuits, list):
            ipm = ion_pass_manager()
            return [ipm.run(circuit.decompose()) for circuit in circuits]
        else:
            return [ion_pass_manager().run(circuits.decompose())]

    def execute(self, circuits, had_transpiled=False):
        if not had_transpiled:
            circuits = self.transpile(circuits)
        counts = {}
        for circuit in circuits:
            jcircuit = jaqal_circuit_from_qiskit_circuit(
                circuit, **self.transpiler_args
            )
            results = run_jaqal_circuit(jcircuit)
            probs = np.array(results.subcircuits[0].probability_by_int)
            qubits = len(circuit.qubits)
            shots = [
                f"{np.random.choice(2 ** qubits, p=probs):b}".zfill(qubits)
                for shot in range(self._run_config.shots)
            ]
            counts[circuit.name] = dict(Counter(shots))
        # job = IonJob(self.backend, "")
        # job._result = IonResult(statevectors)
        return IonResult(counts)


def get_ion_instance(jaqal_backend=None):
    """
    Creates a `qiskit.utils.QuantumInstance` representing the Jaqal emulator backend. Pass it
    to a Qiskit Aqua algorithm or use it to transpile and emulate circuits directly with
    its `execute` method. In the latter case, it will return a result object which can be
    inspected with `get_counts` just as any other Qiskit result object.

    .. warning::
        The current implementation of this function returns a subclass of
        `QuantumInstance`. What subclass if any is returned, and any methods it may have
        in addition to those provided by a `qiskit.utils.QuantumInstance`, are internal
        implementation details and should not be relied on.

    :param jaqal_backend: Pass a backend instance to use. If omitted, instantiates a new
        :class:`jaqalpaq.emulator.UnitarySerializedEmulator`, which in practice should
        usually be the desired usage.
    :type jaqal_backend: :class:`jaqalpaq.emulator.AbstractBackend` or None
    :returns: A Qiskit representation of the Jaqal emulator.
    :rtype: `qiskit.utils.QuantumInstance`
    """
    return IonInstance(Aer.get_backend("qasm_simulator"), jaqal_backend=jaqal_backend)
