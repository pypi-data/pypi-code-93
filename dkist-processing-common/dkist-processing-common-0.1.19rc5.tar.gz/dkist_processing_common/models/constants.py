"""
Components of the Constant model
"""
from enum import Enum


class BudName(str, Enum):
    """
    Controlled list of names for constant stems (buds)
    """

    instrument = "INSTRUMENT"
    num_cs_steps = "NUM_CS_STEPS"
    num_modstates = "NUM_MODSTATES"
    proposal_id = "PROPOSAL_ID"
    average_cadence = "AVERAGE_CADENCE"
    maximum_cadence = "MAXIMUM_CADENCE"
    minimum_cadence = "MINIMUM_CADENCE"
    variance_cadence = "VARIANCE_CADENCE"
    time_order = "TIME_ORDER"
    num_dsps_repeats = "NUM_DSPS_REPEATS"
    spectral_line = "SPECTRAL_LINE"
