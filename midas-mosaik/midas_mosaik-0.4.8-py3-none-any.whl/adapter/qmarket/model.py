# qmarket.py
"""
Minimalistic reactive power market based on sensitivity calculation
(not optimization)

- Does not use voltage measurements, but calculates them instead for Q=0
- sensitivity is calculated once at the beginning of each step
- Over- and undervoltage at the same time not implemented yet
- PU-nodes/pandapower gens not implemented/tested yet

TODO:
- clean sens calculation
- clean market clearing
- add P to sens calc
- Deal with double voltage violation
- Loads auch als Anbieter berücksichtigen? (Vorzeichen!)
- Dokumentation ergänzen / README füllen
- Add PU-nodes to sensitivity calculation
- u_min/max als params umsetzen statt hardgecodet!


Author: Thomas Wolgast <thomas.wolgast@uol.de>

"""

from collections import defaultdict

import numpy
import pandapower as pp
from pandapower.pypower.bustypes import bustypes
from pandapower.pd2ppc import _pd2ppc
import scipy
from midas.adapter.qmarket import LOG

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.WARNING)


class QMarketModel:
    def __init__(self, params):
        self.net = None
        self.agent_bus_map = params["agent_bus_map"]
        self.u_max = params["u_max"]
        self.u_min = params["u_min"]

    def step(self, grid_state, q_offers):
        """Collect all reactive power offers, find offers that solve
        voltage problems in the cheapest way, and return what reactive power
        values should be set."""

        LOG.info(f"Offers from agents: {q_offers}")
        # Default setting: accept no offers (=minimal costs)
        self.q_accept = defaultdict(float)

        self.net = grid_state
        # Reset all q-values to baseline to perform market clearing
        self.net.sgen.q_mvar = 0.0
        self.sensitivity = get_sensitivity(self.net)["dUdQ"]
        LOG.info(self.net.res_bus.vm_pu)
        LOG.debug(self.sensitivity)

        # Check for violations
        overvolt = max(self.net.res_bus.vm_pu) > self.u_max
        undervolt = min(self.net.res_bus.vm_pu) < self.u_min

        if not overvolt and not undervolt:
            # No voltage violation -> no q-demand
            return

        if overvolt and undervolt:
            raise ValueError(
                "Overvoltage and undervoltage at the same time not yet implemented"
            )
            # TODO: try to clear both at the same time? Or one after the other? Difficult to solve without optimization!
        elif undervolt:
            LOG.info("Undervoltage situation!")
            violated_bus = self.net.res_bus.vm_pu.idxmin()
            sorted_offers = self._sort_offers(
                self.sensitivity, q_offers, violated_bus
            )[0]
            constraint = self.u_min
        elif overvolt:
            LOG.info("Overvoltage situation!")
            violated_bus = self.net.res_bus.vm_pu.idxmax()
            sorted_offers = self._sort_offers(
                self.sensitivity, q_offers, violated_bus
            )[1]
            constraint = self.u_max

        # How big is required voltage change?
        if overvolt:
            # Sensitivity value is assumed to be const, but is actually not!
            # 3 % is a good estimation to counteract negative effects of
            # that phenomenon.
            factor = 0.97
        elif undervolt:
            factor = 1.03
        delta_u_set = factor * (
            constraint - self.net.res_bus.vm_pu[violated_bus]
        )

        # Accept all offers until delta_u_set is achieved to clear violation
        for agent_id, max_delta_u, price in sorted_offers:
            # Accept offer
            offering_bus = self._get_offering_bus(agent_id)
            if undervolt:
                self.q_accept[agent_id] += (
                    min(max_delta_u, delta_u_set)
                    / self.sensitivity[violated_bus][offering_bus]
                )
            elif overvolt:
                self.q_accept[agent_id] += (
                    max(max_delta_u, delta_u_set)
                    / self.sensitivity[violated_bus][offering_bus]
                )
                LOG.info(
                    f"market accept from {agent_id}: ", self.q_accept[agent_id]
                )

            # Check whether clearing is be expected to be successful
            if ((max_delta_u < delta_u_set) and overvolt) or (
                (max_delta_u > delta_u_set) and undervolt
            ):
                break

            # Update required voltage delta for next offer
            delta_u_set -= max_delta_u
            # TODO: update sens again to be more precise?

        LOG.info(f"Accepted q-values: {self.q_accept}")
        # Eval: delete!
        # for idx in self.net.sgen.index:
        #     for agent_id, q_value in self.q_accept.items():
        #         bus = self._get_offering_bus(agent_id)
        #         if self.net.sgen.bus[idx] == bus:
        #             self.net.sgen.q_mvar[idx] += q_value
        #             continue
        # pp.runpp(self.net)
        # logger.debug(self.net.res_bus.vm_pu)

    def _get_offering_bus(self, agent_id):
        """Assumption: The market model gets a mapping agent_id<->bus
        at init time."""
        return self.agent_bus_map[agent_id]

    def _sort_offers(self, sens, q_offers: dict, violated_bus: int):
        """Create sorted lists starting with least expensive reactive power
        to most expensive to clear a violation at a given bus."""
        overvolt_offers = []
        undervolt_offers = []
        for ict_channel_id, offers in q_offers.items():
            for offer in offers:
                agent_id = offer["agent_id"]
                offering_bus = self._get_offering_bus(agent_id)
                sens_value = sens[violated_bus][offering_bus]
                # The higher the sensitivity the lower the q-demand
                # -> sensitivity^-1=weight!
                weighted_price = offer["q_price"] / sens_value
                max_delta_u = (offer["q_max"] - offer["q_min"]) * sens_value

                if offer["q_min"] <= 0 and offer["q_max"] <= 0:
                    overvolt_offers.append(
                        (agent_id, -max_delta_u, -weighted_price)
                    )
                elif offer["q_min"] >= 0 and offer["q_max"] >= 0:
                    undervolt_offers.append(
                        (agent_id, max_delta_u, weighted_price)
                    )
                else:
                    raise ValueError(
                        "Offers must be clearly in the positive or negative range (TODO)"
                    )
                    # TODO: How to deal with offer (-10, 10, price). forbid?

        overvolt_offers.sort(key=lambda tup: tup[2])
        undervolt_offers.sort(key=lambda tup: tup[2])

        return undervolt_offers, overvolt_offers


def get_sensitivity(net):
    """Building the sensitivity matrix for a given net.

    dU_i = S_i,j * dQ_j -> S_i,j = sens['dUdQ'][i][j]
    """

    # Wie gehe ich mit PU-Knoten um? Haben keine Sens! -> TODO: testen
    pp.runpp(net, enforce_q_lims=True)

    J = net._ppc["internal"]["J"]
    # Inverse of the Jacobian equals the sensitivity matrix
    J_inv = scipy.sparse.linalg.inv(scipy.sparse.csc_matrix(J))

    # Get bus mapping from internal data structures
    _, ppci = _pd2ppc(net)
    ref, pv, pq = bustypes(ppci["bus"], ppci["gen"])
    pvpq = numpy.r_[pv, pq]

    # Number of (electrically different) buses
    n_PUPQ = len(pvpq)
    n_PQ = len(pq)
    try:
        slack_bus = int(ref)
    except TypeError:
        raise TypeError("Only one external grid possible at the moment!")

    # Extract both sub-matrices from inverse jacobian
    dUdQ = J_inv[n_PUPQ : n_PUPQ + n_PQ, n_PUPQ : n_PUPQ + n_PQ].toarray()
    # dUdP = J_inv[n_PUPQ:n_PUPQ+n_PQ, 0:n_PUPQ].toarray()

    # Assign "electrical" buses to "real" buses
    ppc_indices = list(net._pd2ppc_lookups["bus"])
    """ Example: [0, 1, 1, 2, 2, 3, 4] means "real" buses 1 and 2 are
    electrically equivalent -> both are "electrical bus" 1. The same goes
    for "real" buses 3 and 4 (both together are "electrical bus" 2).
    compare: https://github.com/e2nIEE/pandapower/blob/develop/tutorials/
    internal_datastructure.ipynb """

    for idx, num in enumerate(ppc_indices):
        ppc_indices[idx] = num.item()  # Convert to "normal" integers

    # Reduce multiple buses which are electrical identical to singular bus
    n_PUPQ_trans = len(set(ppc_indices)) - 1  # Minus slack bus
    if net._pd2ppc_lookups["gen"] is None:
        # No generator buses
        n_PU_trans = 0
    else:
        # TODO: Darf es überhaupt PU-Knoten geben? -> Testen + ergänzen!
        n_PU_trans = len(set(net._pd2ppc_lookups["gen"]))
    n_PQ_trans = n_PUPQ_trans - n_PU_trans

    # Sensitivity matrix must be transformed to pd (currently ppc)!
    sens = {}
    # Get sensitivity from "real" electrical buses
    sens["dUdQ"] = [
        list(dUdQ[bus_idx, :n_PQ_trans]) for bus_idx in range(n_PQ_trans)
    ]
    # Add sensitivity of Slack bus (=0)
    sens["dUdQ"].insert(slack_bus, list(numpy.zeros(n_PUPQ_trans)))
    for idx, vector in enumerate(sens["dUdQ"]):
        sens["dUdQ"][idx].insert(slack_bus, 0.0)

    # TODO: Add other submatrices
    # sens['dUdP'] = [list(dUdP[bus_idx, :n_PUPQ_trans])
    #                       for bus_idx in range(n_PQ_trans)]

    return sens
