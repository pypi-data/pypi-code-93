# Copyright 2019-2021 Cambridge Quantum Computing
#
# You may not use this file except in compliance with the Licence.
# You may obtain a copy of the Licence in the LICENCE file accompanying
# these documents or at:
#
#     https://cqcl.github.io/pytket/build/html/licence.html

from pytket import Circuit
from pytket.circuit import PauliExpBox, CircBox  # type: ignore
from pytket.partition import (  # type: ignore
    term_sequence,
    PauliPartitionStrat,
    GraphColourMethod,
)
from .operators import QubitPauliOperator


def gen_term_sequence_circuit(
    operator: QubitPauliOperator,
    reference_state: Circuit,
    partition_strat: PauliPartitionStrat = PauliPartitionStrat.CommutingSets,
    colour_method: GraphColourMethod = GraphColourMethod.Lazy,
) -> Circuit:
    """Sequences QubitPauliOperator terms to generate a circuit made of CircBoxes.
    Each CircBox contains a sequence of PauliExpBox objects.

    :param operator: The operator terms to sequence
    :type operator: QubitPauliOperator
    :param reference_state: reference state to add sequenced terms to.
    :type reference_state: Circuit
    :param partition_strat: a Partition strategy
    :type partition_strat: PauliPartitionStrat, optional
    """
    qps_list = list(operator._dict.keys())
    qps_list_list = term_sequence(qps_list, partition_strat, colour_method)
    n_qbs = reference_state.n_qubits
    circ = reference_state.copy()
    qbs = circ.qubits
    for out_qps_list in qps_list_list:
        circ_to_box = Circuit(n_qbs)
        for qps in out_qps_list:
            coeff = operator[qps]
            qps_map = qps.to_dict()
            if qps_map:
                qubits = list()
                paulis = list()
                for qb, pauli in qps_map.items():
                    qubits.append(qb)
                    paulis.append(pauli)
                pbox = PauliExpBox(paulis, coeff)
                circ_to_box.add_pauliexpbox(pbox, qubits)
            else:
                circ_to_box.add_phase(-coeff / 2)
        cbox = CircBox(circ_to_box)
        circ.add_circbox(cbox, qbs)
    return circ
