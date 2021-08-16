#!/usr/bin/env python
#coding:utf-8

import sys
import math
import struct
import socket
from binascii import hexlify

try:
    import mmap
except ImportError:
    # pylint: disable=invalid-name
    mmap = None

if sys.version_info.major >= 3:
    from itertools import zip_longest as zip_l
else:
    from itertools import izip_longest as zip_l

class IPSrvDB():
    def __init__(self, name, mode="MEMORY"):
        if (mode == "AUTO" and mmap) or mode == "MMAP":
            with open(name, 'rb') as db_file:
                self._buffer = mmap.mmap(db_file.fileno(), 0, access=mmap.ACCESS_READ)
                self._buffer_size = self._buffer.size()
        elif mode == "MEMORY":
            with open(name, 'rb') as db_file:
                self._buffer = db_file.read()
                self._buffer_size = len(self._buffer)
        else:
            raise ValueError(
                'Unsupported open mode ({0}). Only MODE_AUTO '
                'MODE_MEMORY are supported by the pure Python '
                'Reader'.format(mode))

        try:
            self.index_size = struct.unpack('Q', self._buffer[0:8])[0]
            self.data_size = struct.unpack('Q', self._buffer[8:16])[0]
            self.header_size = struct.unpack('H', self._buffer[16:18])[0]

            self.index_end = 18 + self.index_size * 24 # 16B IP + 8B index
            data_end = self.index_end + self.data_size
            # self._index = self._buffer[18:self.index_end]
            # self._data = self._buffer[self.index_end:data_end]

            header_end = data_end + self.header_size
            self.header = self._buffer[data_end:header_end].decode('utf-8').strip().split(',')
            self.date = self._buffer[header_end:header_end+8]
            self.description = self._buffer[header_end+8:]
        except (IndexError, UnicodeDecodeError):
            raise Exception("Invalid dat file!\n")

    def index(self, start, end):
        # if start > end or end > index_end:
        #     return None
        # 18 为 index_size + data_size + header_size
        return self._buffer[start+18:end+18]

    def data(self, start, end):
        # if start > end or end > self.data_size:
        #    return None
        return self._buffer[start+self.index_end:end+self.index_end]

    def ip_to_int(self, ipstr):
        if ":" in ipstr:
            return int(hexlify(socket.inet_pton(socket.AF_INET6, ipstr)), 16)
        else:
            return socket.ntohl(struct.unpack("I",socket.inet_aton(str(ipstr)))[0])
        
    def find(self, ip):
        ipint = self.ip_to_int(ip)
        start = 0
        mid = 0
        end = self.index_size - 1
        while start <= end:
            mid = int((start + end) / 2)

            high, low = struct.unpack('>QQ', self.index(mid*24, mid*24+16))
            unpacked  = (high << 64) | low
            if unpacked > ipint :
                end = mid
            elif unpacked < ipint:
                start = mid
                if start == end - 1:
                    offset = struct.unpack('II', self.index(mid*24+16, mid*24+24))
                    return self.data(offset[0], offset[0]+offset[1])
            elif unpacked == ipint:
                offset = struct.unpack('II', self.index(mid*24+16, mid*24+24))
                return self.data(offset[0], offset[0]+offset[1])

    def findx(self, ip):
        data = self.find(ip).decode('utf-8').strip('\x00').strip().split(',')
        result = dict(zip_l(self.header, data, fillvalue=''))
        return result

    def get_header(self):
        return self.header

    def get_date(self):
        return self.date

    def get_description(self):
        return self.description
