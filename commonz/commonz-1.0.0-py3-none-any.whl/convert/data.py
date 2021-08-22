#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide binary data converters"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020-09-20"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



import struct # can convert a number or string to binary data and vice versa
#import binascii # Convert binary to ASCII and vice versa



def decode(data,format):
	"""returns the decoded binary data"""
	### '!' represents the network byte order which is always big-endian as defined in IETF RFC1700
	return struct.unpack('!'+format,data)


def encode(data,format):
	"""returns the encoded binary data"""
	### '!' represents the network byte order which is always big-endian as defined in IETF RFC1700
	return struct.pack('!'+format,number)

