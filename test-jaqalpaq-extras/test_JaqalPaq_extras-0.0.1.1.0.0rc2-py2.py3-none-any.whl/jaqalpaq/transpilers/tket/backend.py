# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

# Portions of this work are derived from the pytket extension modules which are
# copyright 2020-2021 Cambridge Quantum Computing and used under the Apache License 2.0.

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
    TYPE_CHECKING,
    Set,
)

from numpy.random import default_rng

from pytket.backends import Backend, CircuitStatus, ResultHandle
from pytket.backends.backendresult import BackendResult
from pytket.backends.backendinfo import BackendInfo
from pytket.backends.resulthandle import _ResultIdTuple
from pytket.backends.status import StatusEnum
from pytket.circuit import OpType, Circuit, Bit, Qubit
from pytket.routing import Architecture
from pytket.passes import (
    BasePass,
    RebaseUMD,
    SynthesiseUMD,
    SequencePass,
    DecomposeBoxes,
    DelayMeasures,
)
from pytket.utils.results import KwargTypes
from pytket.utils.outcomearray import OutcomeArray
from pytket.predicates import (
    Predicate,
    NoSymbolsPredicate,
    GateSetPredicate,
    NoMidMeasurePredicate,
)

from jaqalpaq import JaqalError
from jaqalpaq.emulator import UnitarySerializedEmulator, run_jaqal_circuit
from jaqalpaq.emulator.backend import AbstractBackend
from jaqalpaq.core.result import ExecutionResult, ProbabilisticSubcircuit
from .frontend import _TKET_NAMES, jaqal_circuit_from_tket_circuit

extension_version = "1.0"


class JaqalBackend(Backend):
    """
    A t|ket> backend representation of the Jaqal emulator. Does not support circuits with
    multiple subcircuits. Except as described below, this conforms in all respects to the
    t|ket> backend API; see its documentation for details and usage.

    :param str backend_name: Label this backend for internal t|ket> reference.
    :param emulator: Pass a backend instance to use. If omitted, instantiates a new
        :class:`jaqalpaq.emulator.UnitarySerializedEmulator`, which in practice should
        usually be the desired usage.
    :type emulator: :class:`jaqalpaq.emulator.AbstractBackend` or None
    """

    _persistent_handles = False
    _supports_shots = True
    _supports_counts = True
    _supports_expectation = False
    _expectation_allows_nonhermitian = False

    def __init__(self, backend_name: str, emulator: Optional[AbstractBackend] = None):
        super().__init__()
        if emulator is None:
            emulator = UnitarySerializedEmulator()
        self._emulator: AbstractBackend = emulator

        gate_set: Set[OpType] = set(_TKET_NAMES.keys())
        self._backend_info = BackendInfo(
            type(self).__name__,
            backend_name,
            extension_version,
            Architecture([]),
            gate_set,
            supports_midcircuit_measurement=False,  # is this correct?
            misc={"characterisation": None},
        )

        self._memory = False

        self._rebase_pass = RebaseUMD()

    @property
    def _result_id_type(self) -> _ResultIdTuple:
        return (int,)

    @property
    def characterisation(self) -> Optional[Dict[str, Any]]:
        char = self._backend_info.get_misc("characterisation")
        return cast(Dict[str, Any], char) if char else None

    @property
    def backend_info(self) -> BackendInfo:
        return self._backend_info

    def process_circuits(
        self,
        circuits: Sequence[Circuit],
        n_shots: Optional[Union[int, Sequence[int]]] = None,
        valid_check: bool = True,
        **kwargs: KwargTypes,
    ) -> List[ResultHandle]:
        circuits = list(circuits)
        n_shots_list: List[Optional[int]] = []
        if hasattr(n_shots, "__iter__"):
            n_shots_list = cast(List[Optional[int]], n_shots)
            if len(n_shots_list) != len(circuits):
                raise ValueError("The length of n_shots and circuits must match")
        else:
            # convert n_shots to a list
            n_shots_list = [cast(int, n_shots)] * len(circuits)

        if valid_check:
            self._check_all_circuits(circuits)

        handle_list: List[Optional[ResultHandle]] = [None] * len(circuits)

        for n_shots, tkc, i in zip(n_shots_list, circuits, range(len(circuits))):
            jc = jaqal_circuit_from_tket_circuit(tkc, remove_measurements=True)
            jaqal_result = run_jaqal_circuit(jc, self._emulator)
            handle = ResultHandle(i)
            handle_list[i] = handle
            self._cache[handle] = {
                "result": self._process_result(jaqal_result, n_shots or 1)
            }
        return cast(List[ResultHandle], handle_list)

    def circuit_status(self, handle: ResultHandle) -> CircuitStatus:
        return StatusEnum.COMPLETED
        # We're running synchronously so if you can call this method, the job's done.

    @property
    def required_predicates(self) -> List[Predicate]:
        pred_list = [
            NoSymbolsPredicate(),
            NoMidMeasurePredicate(),
            GateSetPredicate(
                self._backend_info.gate_set.union(
                    {
                        OpType.Measure,
                        OpType.Reset,
                        OpType.Barrier,
                        OpType.noop,
                        OpType.CircBox,
                        OpType.ExpBox,
                        OpType.PauliExpBox,
                        OpType.RangePredicate,
                    }
                )
            ),
        ]
        return pred_list

    def default_compilation_pass(self, optimisation_level: int = 1) -> BasePass:
        assert optimisation_level in range(3)
        passlist = [DecomposeBoxes()]
        if optimisation_level == 0:
            passlist.append(self._rebase_pass)
        elif optimisation_level >= 1:
            passlist.append(SynthesiseUMD())
        passlist.append(DelayMeasures())
        return SequencePass(passlist)

    def _process_result(self, result: ExecutionResult, n_shots: int) -> BackendResult:
        c_bits = [
            Bit("measurement", shot, bit)
            for bit in range(len(result.subcircuits[0].measured_qubits))
            for shot in range(len(result.readouts))
        ]
        q_bits = [
            Qubit(bit)
            for bit in range(len(result.readouts[0].subcircuit.measured_qubits))
        ]
        if n_shots == 1:
            shots = OutcomeArray.from_readouts(
                [[int(bit) for shot in result.readouts for bit in shot.as_str]]
            )
        elif isinstance(result.subcircuits[0], ProbabilisticSubcircuit):
            rng = default_rng()

            def _generate_outcome(probs):
                return rng.choice(list(probs.keys()), p=list(probs.values()))

            shots = OutcomeArray.from_readouts(
                [
                    [
                        int(bit)
                        for readout in result.readouts
                        for bit in _generate_outcome(
                            readout.subcircuit.probability_by_str
                        )
                    ]
                    for shot in range(n_shots)
                ]
            )
        else:
            raise JaqalError(
                "Cannot sample multiple shots from data; use loop instead."
            )
        return BackendResult(
            c_bits=c_bits,
            q_bits=q_bits,
            shots=shots,
            counts=None,
            state=None,
            unitary=None,
            ppcirc=None,
        )
