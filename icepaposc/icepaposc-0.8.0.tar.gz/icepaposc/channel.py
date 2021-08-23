#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# This file is part of IcepapOCS link:
#        https://github.com/ALBA-Synchrotron/IcepapOCS
#
# Copyright 2017:
#       MAX IV Laboratory, Lund, Sweden
#       CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Distributed under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#
# You should have received a copy of the GNU General Public License
# along with IcepapOCS. If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------


class Channel:
    """A container class holding information for a driver signal."""

    def __init__(self, address, signal_name):
        """
        Initializes an instance of class Channel.

        address     - IcePAP driver id.
        signal_name - Signal name.
        """
        self.icepap_address = address
        self.sig_name = signal_name
        self.measure_resolution = 1.
        self.collected_samples = []

    def equals(self, icepap_addr, signal_name):
        """
        Checks for equality.

        icepap_addr - IcePAP address.
        signal_name - Signal name.
        Return: True if equal. False otherwise.
        """
        if icepap_addr != self.icepap_address:
            return False
        if signal_name != self.sig_name:
            return False
        return True

    def set_measure_resolution(self, cfg):
        """
        Set measure resolution.

        cfg - Config info extracted from IcePAP.
        """
        tgtenc = cfg['TGTENC'].upper()
        shftenc = cfg['SHFTENC'].upper()
        axisnstep = cfg['ANSTEP']
        axisnturn = cfg['ANTURN']
        nstep = axisnstep
        nturn = axisnturn
        if tgtenc == 'ABSENC' or (tgtenc == 'NONE' and shftenc == 'ABSENC'):
            nstep = cfg['ABSNSTEP']
            nturn = cfg['ABSNTURN']
        elif tgtenc == 'ENCIN' or (tgtenc == 'NONE' and shftenc == 'ENCIN'):
            nstep = cfg['EINNSTEP']
            nturn = cfg['EINNTURN']
        elif tgtenc == 'INPOS' or (tgtenc == 'NONE' and shftenc == 'INPOS'):
            nstep = cfg['INPNSTEP']
            nturn = cfg['INPNTURN']
        self.measure_resolution = (float(nstep) / float(nturn)) / \
                                  (float(axisnstep) / float(axisnturn))
