#!/usr/bin/env python3
#
# Copyright 2021 NXP
# SPDX-License-Identifier: BSD-3-Clause
#
# NXP USBSIO Library to control SPI, I2C and GPIO bus over USB
#
__version__ = '2.1.5'
__title__ = 'usblibsio'
__author__ = 'NXP Semiconductors'
__copyright__ = 'Copyright NXP 2021'
__license__ = 'BSD-3-Clause'
__url__ = 'https://www.nxp.com/design/development-boards/lpcxpresso-boards/mcu-link-debug-probe:MCU-LINK'
__description__ = 'Python interface for the NXP USBSIO Library.'
__long_description__ = '''LIBUSBSIO: The NXP USBSIO Library
This module implements a Python wrapper around the NXP USBSIO Library enabling to access SPI or
I2C bus and GPIO ports over a USB interface of the NXP LPC-link2 and MCU-Link devices.
'''

from .libusbsio import *
