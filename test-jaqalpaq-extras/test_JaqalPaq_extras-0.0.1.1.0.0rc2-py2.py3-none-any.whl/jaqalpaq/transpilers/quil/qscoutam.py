# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
from pyquil.api import QAM

from jaqalpaq import JaqalError


class QSCOUTAM(QAM):
    """
    Quantum Abstract Machine representing the QSCOUT hardware. It will refuse to load or
    run programs, but can be used as a compilation target. Instead of using the Quil API
    to load and run programs, instead compile them to Jaqal files and submit them to
    the QSCOUT team directly.
    """

    def load(self, executable):
        """
        Does not load a Jaqal program onto an abstraction of the QSCOUT hardware.

        :raises JaqalError: Because the Quil API should not be used to try to execute programs on QSCOUT.
        """
        raise JaqalError(
            "QSCOUT cannot run programs through the Quil API. Generate a Jaqal file with compile() and submit it directly to the QSCOUT team."
        )

    def run(self):
        """
        Does not run a previously loaded Jaqal program on an abstraction of the QSCOUT hardware.

        :raises JaqalError: Because the Quil API should not be used to try to execute programs on QSCOUT.
        """
        raise JaqalError(
            "QSCOUT cannot run programs through the Quil API. Generate a Jaqal file with compile() and submit it directly to the QSCOUT team."
        )
