#!/usr/bin/env python
"""dll_bitsize.py"""

import os
import struct
import sys


def arch_of(dll_file):
	"""adapted from: http://stackoverflow.com/a/495305/1338797"""
	with open(dll_file, "rb") as dll:
		doshdr = dll.read(64)
		magic, _padding, offset = struct.unpack("2s58si", doshdr)
		# print magic, offset
		if magic != b"MZ":
			return None
		dll.seek(offset, os.SEEK_SET)
		pehdr = dll.read(6)
		# careful! H == unsigned short, x64 is negative with signed
		magic, _padding, machine = struct.unpack("2s2sH", pehdr)
		# print magic, hex(machine)
		if magic != b"PE":
			return None
		if machine == 0x014C:
			return "i386"
		if machine == 0x0200:
			return "IA64"
		if machine == 0x8664:
			return "x64"
		return "unknown"


print(arch_of(sys.argv[1]))
