#!/bin/env python3
# -*- coding: utf-8 -*-
# pyi2c.py
"""
A useful I2C class and functions
"""
__author__      = "Eunchong Kim"
__copyright__   = "Copyright 2021, Eunchong Kim"
__credits__     = ["Eunchong Kim"]
__license__     = "GPL"
__version__     = "1.0.0"
__maintainer__  = "Eunchong Kim"
__email__       = "chariskimec@gmail.com"
__status__      = "Production"


# =================================================
import enum, logging
# Require smbus2 to communicate
from smbus2 import SMBus, i2c_msg


# =================================================
class StatusCode(enum.Enum):
    """
    Status code
    """
    success = 0
    ready   = 1
    fail    = 9


# =================================================
class I2C:
    """
    A simple i2c interface by using smbus2, for Pi.
    """
    def __init__(self, bus_n=0):
        self._bus_n = bus_n
        self._bus = SMBus(bus_n)
        self._status_code = StatusCode.ready

    # Status code can be accessed
    @property
    def status_code(self):
        return self._status_code

    # Scan all I2C devices on the bus
    def scan(self):
        addr_list = []
        output_str = "    "
        for x in range(0xf+1):
            output_str += '%02x ' % x
        logging.info(output_str)
        for y in range(0x8+1):
            output_str = '%02x: ' % (y << 4)
            for x in range(0xf+1):
                addr = (y << 4) + x
                try:
                    self._bus.i2c_rdwr( i2c_msg.read(addr, 1) )
                    addr_list.append(addr)
                    output_str += '%02x ' % addr
                except:
                    output_str += '-- '
            logging.info(output_str)
        self._status_code = StatusCode.success
        return addr_list

    # Write data
    def write(self, addr, data):
        if not type(data) == list:
            data = [ data ]
        write_msg = i2c_msg.write(addr, data)
        try:
            self._bus.i2c_rdwr(write_msg)
            self._status_code = StatusCode.success
        except Exception as e:
            self._status_code = StatusCode.fail
            logging.error('Cannot write on bus: %d, addr: %s. %s'
                    % (self._bus_n, hex(addr), e) )

    # Read bytes of data
    def read(self, addr, byte_size=1):
        read_msg = i2c_msg.read(addr, byte_size)
        try:
            self._bus.i2c_rdwr(read_msg)
            self._status_code = StatusCode.success
        except Exception as e:
            self._status_code = StatusCode.fail
            logging.error('Cannot read on bus: %d, addr: %s. %s'
                    % (self._bus_n, hex(addr), e) )
        # List of i2c_msg should be converted to list of bytes
        read_data = list(read_msg)
        return read_data[0] if len(read_data) == 1 else read_data

    # Write data and read bytes of data soon
    def writeread(self, addr, data, byte_size=1):
        if not type(data) == list:
            data = [ data ]
        write_msg = i2c_msg.write(addr, data)
        read_msg = i2c_msg.read(addr, byte_size)
        try:
            self._bus.i2c_rdwr(write_msg, read_msg)
            self._status_code = StatusCode.success
        except Exception as e:
            self._status_code = StatusCode.fail
            logging.error('Cannot writeread on bus: %d, addr: %s. %s'
                    % (self._bus_n, hex(addr), e) )
        # List of i2c_msg should be converted to list of bytes
        read_data = list(read_msg)
        return read_data[0] if len(read_data) == 1 else read_data


# =================================================
class I2CDevice:
    """
    A simple I2C device class which uses I2C.
    Do not need to input address on its function.
    """
    def __init__(self, bus_n, addr):
        self._i2c = I2C(bus_n)
        self._addr = addr

    @property
    def status_code(self):
        return self._i2c.status_code

    def write(self, data):
        self._i2c.write(self._addr, data)

    def read(self, byte_size=1):
        return self._i2c.read(self._addr, byte_size)

    def writeread(self, data, byte_size=1):
        return self._i2c.writeread(self._addr, data, byte_size)


# =================================================
# Get bits from #n to #m of the bytes data
def getBit(byte, bit_n, bit_m=-1):
    # bit_m can be empty
    if bit_m < 0:
        bit_m = bit_n
    bit = 0
    for i in range( abs(bit_n - bit_m) + 1 ):
        bit += 0 if byte & 2**(min(bit_n, bit_m)+i) == 0 else 1 * 2**i
    return bit


# =================================================
def main():
    pass


if __name__ == '__main__':
    main()
