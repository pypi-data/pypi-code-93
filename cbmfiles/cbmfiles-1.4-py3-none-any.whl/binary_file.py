import struct


class BinaryFile:
    def __init__(self, fileh, start_addr=None):
        if start_addr is None and fileh is not None:
            # read start address from file
            self.start_addr, = struct.unpack('<H', fileh.read(2))
        else:
            self.start_addr = start_addr
        self.data = fileh.read()

    def to_text(self):
        """Generator to format file contents as hex dump."""
        addr = self.start_addr

        data = self.data
        while data:
            current = data[:16]
            fmt = "${:04x}: "
            fmt += " {:02x}" * len(current)
            pack = "<{}B".format(len(current))
            yield fmt.format(addr, *struct.unpack(pack, current))
            addr += len(current)
            data = data[16:]
