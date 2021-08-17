""" module:: Socketcan
    :platform: Posix
    :synopsis: An abstraction to socketcan interface using python objects
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: GPL v3
"""

import socket
import struct

from enum import IntEnum, IntFlag
from typing import Sequence, Union, Tuple, Optional
from io import DEFAULT_BUFFER_SIZE
import logging

LOGGER = logging.getLogger("socketcan")

try:
    # The flags and defines for ISOTP are missing in socket module right now!
    from socket import CAN_ISOTP_TX_PADDING, CAN_ISOTP_RX_PADDING, SOL_CAN_ISOTP, CAN_ISOTP_OPTS, \
        CAN_ISOTP_WAIT_TX_DONE, CAN_ISOTP_LISTEN_MODE
except ImportError:
    LOGGER.error("ImportError on isotp CAN constants")
    CAN_ISOTP_LISTEN_MODE = 0x001
    CAN_ISOTP_TX_PADDING = 0x004
    CAN_ISOTP_RX_PADDING = 0x008
    CAN_ISOTP_WAIT_TX_DONE = 0x400
    SOL_CAN_ISOTP = 106
    CAN_ISOTP_OPTS = 1


class BcmOpCodes(IntEnum):
    TX_SETUP = 1
    TX_DELETE = 2
    TX_READ = 3
    RX_SETUP = 5
    RX_DELETE = 6
    RX_READ = 7
    RX_STATUS = 10
    RX_TIMEOUT = 11
    RX_CHANGED = 12


class BCMFlags(IntFlag):
    SETTIMER = 0x01
    STARTTIMER = 0x02
    RX_FILTER_ID = 0x20


class CanFlags(IntFlag):
    CAN_ERR_FLAG = 0x20000000
    CAN_RTR_FLAG = 0x40000000
    CAN_EFF_FLAG = 0x80000000


class CanFdFlags(IntFlag):
    CAN_FD_BIT_RATE_SWITCH = 0x01
    CAN_FD_ERROR_STATE_INDICATOR = 0x02


def float_to_timeval(val: float) -> Tuple[int, int]:
    """
    Helper function to convert timeval

    :param val: The timeval as float.
    :return: The seconds and microseconds of the timeval.
    """
    sec = int(val)
    usec = int((val - sec) * 1000000)
    return sec, usec


def timeval_to_float(sec: int, usec: int) -> float:
    """
    Helper function to convert timeval

    :param sec: The seconds of the timeval.
    :param usec: The microseconds of the timeval.
    :return: The timeval as float.
    """
    return sec + (usec / 1000000)


def combine_can_id_and_flags(can_id: int, flags: CanFlags = 0) -> int:
    """
    Helper function to convert can_id and flags
    to the can_id which socketcan uses.

    :param can_id: The can_id as integer.
    :param flags: The flags to be set, i.e. EFF for can_ids > 0x7FF
    :return: The can_id which socketcan uses.
    """
    can_id_with_flags = (can_id | flags)
    return can_id_with_flags


def split_can_id_and_flags(can_id_with_flags: int) -> Tuple[int, int]:
    """
    Helper function to split the can_id which socketcan
    uses into can_id and flags.

    :param can_id_with_flags: The can_id which socketcan uses.
    :return: A tuple of can_id and flags.
    """
    flags = CanFlags(can_id_with_flags & 0xE0000000)
    can_id = (can_id_with_flags & 0x1FFFFFFF)
    return can_id, flags


class CanFrame:
    """ A CAN frame or message, low level calls it frame, high level calls it a message.
    
        :param can_id: the can bus id of the frame, integer in range 0-0x1FFFFFFF.
        :param data: the data bytes of the frame.
        :param flags: the flags, the 3 top bits in the MSB of the can_id.
    """

    FORMAT = "IB3x8s"

    def __init__(self,
                 can_id: int,
                 data: bytes,
                 flags: CanFlags = 0,
                 ):
        self.can_id = can_id
        self.flags = flags
        if (can_id > 0x7FF) and not (CanFlags.CAN_EFF_FLAG & self.flags):
            self.flags = self.flags | CanFlags.CAN_EFF_FLAG
        self.data = data

    def to_bytes(self):
        """
        Convert to bytes representation.

        :return: The bytes representation of the object.
        """
        data = self.data
        data.ljust(8)
        return struct.pack(self.FORMAT, combine_can_id_and_flags(self.can_id, self.flags), len(self.data), data)

    def __eq__(self, other) -> bool:
        """
        Standard equality operation.

        :param other: Another CanFrame to compare with self.
        :return: True if equal, False otherwise.
        """
        is_equal = False
        if isinstance(other, CanFrame):
            is_equal = all((self.can_id == other.can_id,
                            self.flags == other.flags,
                            self.data == other.data
                            ))
        return is_equal

    def __ne__(self, other) -> bool:
        """
        Standard non equality operation

        :param other: Another CanFrame to compare with self.
        :return: True if unequal, False otherwise.
        """
        return not self.__eq__(other)

    @classmethod
    def from_bytes(cls, byte_repr):
        """
         Factory to create instance from bytes representation.

        :param byte_repr: The bytes representation of the object.
        :return: An instance of this class.
        """
        assert len(byte_repr) == cls.get_size()
        can_id_with_flags, data_length, data = struct.unpack(cls.FORMAT, byte_repr)
        can_id, flags = split_can_id_and_flags(can_id_with_flags)
        return CanFrame(can_id=can_id,
                        flags=flags,
                        data=data[:data_length])

    @classmethod
    def get_size(cls):
        """
        Get the calculated byte size of this class.

        :return: The size in bytes.
        """
        return struct.calcsize(cls.FORMAT)


class CanFdFrame(CanFrame):
    """ A CAN FD frame, actually a variant of CanFrame

        :param can_id: the can bus id of the frame, integer in range 0-0x1FFFFFFF.
        :param data: the data bytes of the frame.
        :param flags: the flags, the 3 top bits in the MSB of the can_id.
        :param fd_flags: additional flags for can fd, e.g. the baud rate switch.
    """

    FORMAT = "IBB2x64s"

    def __init__(self, can_id: int, data: bytes, flags: CanFlags = CanFlags(0),
                 fd_flags: CanFdFlags = CanFdFlags.CAN_FD_BIT_RATE_SWITCH):
        super().__init__(can_id, data, flags)
        # self.can_id = can_id
        # self.flags = flags
        self.fd_flags = fd_flags
        # if (can_id > 0x7FF) and not (CanFlags.CAN_EFF_FLAG & self.flags):
        #     self.flags = self.flags | CanFlags.CAN_EFF_FLAG
        self.data = data

    def to_bytes(self) -> bytes:
        """
        Convert to bytes representation.

        :return: The bytes representation of the object.
        """
        data = self.data
        data.ljust(64)
        return struct.pack(self.FORMAT, combine_can_id_and_flags(self.can_id, self.flags), len(self.data),
                           self.fd_flags, data)

    def __eq__(self, other) -> bool:
        """
        Standard equality operation.

        :param other: Another CanFrame to compare with self.
        :return: True if equal, False otherwise.
        """
        is_equal = False
        if isinstance(other, CanFdFrame):
            is_equal = all((self.can_id == other.can_id,
                            self.flags == other.flags,
                            self.fd_flags == other.fd_flags,
                            self.data == other.data
                            ))
        return is_equal

    def __ne__(self, other) -> bool:
        """
        Standard non equality operation

        :param other: Another CanFdFrame to compare with self.
        :return: True if unequal, False otherwise.
        """
        return not self.__eq__(other)

    @classmethod
    def from_bytes(cls, byte_repr):
        """
         Factory to create instance from bytes representation.

        :param byte_repr: The bytes representation of the object.
        :return: An instance of this class.
        """
        assert len(byte_repr) == cls.get_size()
        can_id_with_flags, data_length, fd_flags, data = struct.unpack(cls.FORMAT, byte_repr)
        can_id, flags = split_can_id_and_flags(can_id_with_flags)
        return CanFdFrame(can_id=can_id,
                          flags=flags,
                          fd_flags=fd_flags,
                          data=data[:data_length])


class BcmMsg:
    """ Abstract the message to BCM socket.
    
        For tx there are two use cases,
        1. a message to be sent with a defined interval for a defined number of times (count)
            populate opcode, flags, count, interval1, can_id, frame
        2. a message to be sent with a defined interval for the whole time the BcmSocket remains open
            populate opcode, flags, interval2, can_id, frame

        For rx there is X use cases,
        1. receive a message that is sent with a defined interval and be informed about timeout of this message
            populate opcode, flags, can_id, interval1

        :param opcode: operation code of / to BCM
        :param flags: flags of / to BCM
        :param count: a count
        :param interval1: in case of tx this is the time in between each count to transmit the message,
                          in case of rx, this is the timeout value at which RX_TIMEOUT is sent from BCM to user space
        :param interval2: in case of tx, this is the time in between each subsequent transmit after count has exceeded
                          in case of rx, this is a time to throttle down the flow of messages to user space
        :param can_id: of can message
               CAVEAT: THE CAN_FLAGS ARE PART OF CAN_ID HERE, e.g. long can id's are not recognized if flags are not set
                       and comparing the bcm can_id with the frame id fails because the flags have been excluded by
                       concept of CanFrame
        :param frames: an iterable of CanFrames
    """

    # this is a great hack, we force alignment to 8 byte boundary
    # by adding a zero length long long 
    FORMAT = "IIIllllII0q"

    def __init__(self,
                 opcode: BcmOpCodes,
                 flags: BCMFlags,
                 count: int,
                 interval1: float,
                 interval2: float,
                 can_id: int,
                 frames: Sequence[CanFrame],

                 ):
        self.opcode = opcode
        self.flags = flags
        self.count = count
        self.interval1 = interval1
        self.interval2 = interval2
        self.can_id = can_id
        self.frames = frames

    def to_bytes(self) -> bytes:
        """
        Convert to bytes representation.

        :return: The bytes representation of the object.
        """
        interval1_seconds, interval1_microseconds = float_to_timeval(self.interval1)
        interval2_seconds, interval2_microseconds = float_to_timeval(self.interval2)
        byte_repr = bytearray()
        byte_repr.extend(struct.pack(self.FORMAT, self.opcode, self.flags,
                                     self.count, interval1_seconds, interval1_microseconds,
                                     interval2_seconds, interval2_microseconds, self.can_id,
                                     len(self.frames)))
        for frame in self.frames:
            byte_repr.extend(frame.to_bytes())

        return byte_repr

    def __eq__(self, other) -> bool:
        """
        Standard equality operation.

        :param other: Another BcmMsg to compare with self.
        :return: True if equal, False otherwise.
        """
        is_equal = False
        if isinstance(other, BcmMsg):
            is_equal = all((self.opcode == other.opcode,
                            self.flags == other.flags,
                            self.count == other.count,
                            self.interval1 == other.interval1,
                            self.interval2 == other.interval2,
                            self.can_id == other.can_id,
                            self.frames == other.frames,
                            ))
        return is_equal

    def __ne__(self, other) -> bool:
        """
        Standard non equality operation

        :param other: Another BcmMsg to compare with self.
        :return: True if unequal, False otherwise.
        """
        return not self.__eq__(other)

    @classmethod
    def from_bytes(cls, byte_repr: bytes):
        """
        Factory to create instance from bytes representation.

        :param byte_repr: The bytes representation of the object.
        :return: An instance of this class.
        """
        opcode, flags, count, interval1_seconds, interval1_microseconds, interval2_seconds, interval2_microseconds, \
        can_id, number_of_frames = struct.unpack(cls.FORMAT, byte_repr[:cls.get_size()])
        interval1 = timeval_to_float(interval1_seconds, interval1_microseconds)
        interval2 = timeval_to_float(interval2_seconds, interval2_microseconds)
        frames = [CanFrame.from_bytes(byte_repr[idx:idx + CanFrame.get_size()])
                  for idx in range(cls.get_size(), len(byte_repr), CanFrame.get_size())]
        assert len(frames) == number_of_frames
        return BcmMsg(opcode=BcmOpCodes(opcode),
                      flags=BCMFlags(flags),
                      count=count,
                      interval1=interval1,
                      interval2=interval2,
                      can_id=can_id,
                      frames=frames,
                      )

    @classmethod
    def get_size(cls):
        """
        Get the calculated byte size of this class.

        :return: The size in bytes.
        """
        return struct.calcsize(cls.FORMAT)


class CanRawSocket:
    """
    A socket to raw CAN interface.
    """

    def __init__(self,
                 interface: str,
                 use_can_fd: bool = True):
        """
        Constuctor

        :param interface: The interface name.
        :param use_can_fd: Enable socket option for CAN FD.
        """
        self._s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        if use_can_fd:
            self._s.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FD_FRAMES, True)
        self._s.bind((interface,))

    def __del__(self):
        self._s.close()

    def fileno(self):
        return self._s.fileno()

    def send(self, frame: Union[CanFrame, CanFdFrame]) -> int:
        """
        Send a CAN frame.
        
        :param frame: A CanFrame.
        :return: The number of bytes written.
        """
        return self._s.send(frame.to_bytes())

    def recv(self) -> Optional[Union[CanFrame, CanFdFrame]]:
        """
        Receive a CAN (FD) Frame.

        :return: A CAN (FD) Frame instance.
        """
        data = self._s.recv(DEFAULT_BUFFER_SIZE)

        for cls in [CanFrame, CanFdFrame]:
            try:
                frame = cls.from_bytes(data)
            except AssertionError:
                frame = None
            else:
                break
        if frame is None:
            LOGGER.error("Could not create CanFrame from buffer {0}".format(data.hex()))
        return frame


class CanBcmSocket:
    """
    A socket to broadcast manager. Broadcast manager is essentially
    a worker, you can conveniently give transmission tasks like send a cyclic message
    with interval X forever, or just do it a number of times and then quit.
    
    :note: The RX side is mostly untested.
    """

    def __init__(self, interface: str):
        """
        Constuctor

        :param interface: The interface name.
        """
        self._s = socket.socket(socket.PF_CAN, socket.SOCK_DGRAM, socket.CAN_BCM)
        self._s.connect((interface,))

    def __del__(self):
        self._s.close()

    def fileno(self):
        return self._s.fileno()

    def send(self, bcm: BcmMsg):
        """
        Send a bcm message to bcm socket.
        
        :param bcm: A bcm message to be sent.
        :return: The number of bytes written.
        """
        return self._s.send(bcm.to_bytes())

    def recv(self) -> Optional[BcmMsg]:
        """
        Receive a bcm message from bcm socket

        :return: A BcmMsg instance.
        """
        data = self._s.recv(DEFAULT_BUFFER_SIZE)
        try:
            bcm = BcmMsg.from_bytes(data)
        except AssertionError:
            LOGGER.error("Could not create BcmMsg from buffer {0}".format(data.hex()))
            bcm = None
        return bcm

    def setup_cyclic_transmit(self,
                              frame: CanFrame,
                              interval: float) -> int:
        """
        A shortcut function to setup a cyclic transmission
        of a CanFrame.
        
        :param frame: The CanFrame to be sent.
        :param interval: The interval it should be sent.
        :return: The number of bytes written.
        """
        bcm = BcmMsg(opcode=BcmOpCodes.TX_SETUP,
                     flags=(BCMFlags.SETTIMER | BCMFlags.STARTTIMER),
                     count=0,
                     interval1=0,
                     interval2=interval,
                     can_id=frame.can_id,
                     frames=[frame, ],
                     )
        return self.send(bcm)

    def remove_cyclic_transmit(self,
                              frame: CanFrame,
                              ) -> int:
        """
        A shortcut function to remove a cyclic transmission
        of a CanFrame.

        :param frame: The CanFrame to be removed.
        :return: The number of bytes written.
        """
        bcm = BcmMsg(opcode=BcmOpCodes.TX_DELETE,
                     flags=BCMFlags(0),
                     count=0,
                     interval1=0,
                     interval2=0,
                     can_id=frame.can_id,
                     frames=[],
                     )
        return self.send(bcm)

    def setup_receive_filter(self,
                             frame: CanFrame,
                             timeout: float) -> int:
        """
        A shortcut function to setup a receive filter.
        Technically you're setting two filters here. The filter on can_id of the frame and the filter
        on data of the frame. If the can_id of the received frame matches the filter it goes to data
        filtering. Data filtering is XOR'ed with the previous received frame and AND'ed with the data
        filter that you provided with this function by setting the interesting bits to 1 in data.
        What it does then can be configured. With this function it just checks for timeout.
        
        :param frame: A CanFrame instance, the can_id is a filter and the data is a filter.
        :param timeout: The timeout for reception, should be more than the interval of the expected frame.

        :return: The number of bytes written.

        :Note: The can_id in bcm message is used for addressing the filter and can_id compare
               Therefore the can_id must contain the flags.
        """

        can_id = frame.can_id
        can_flags = frame.flags
        if can_flags:
            can_id = can_id | can_flags

        bcm = BcmMsg(opcode=BcmOpCodes.RX_SETUP,
                     flags=(BCMFlags.SETTIMER | BCMFlags.STARTTIMER),
                     count=0,
                     interval1=timeout,
                     interval2=0,
                     can_id=can_id,
                     frames=[frame, ],
                     )
        return self.send(bcm)

    def get_receive_filter(self,
                           can_id: int,
                           can_flags: CanFlags = 0):
        """
        A shortcut function to get the receive filter for a can_id.

        :param can_id: The can_id which the filter is registered for.
        :param can_flags: The can_flags that must be set in the can_id because bcm expects that.

        :Note: The can_id in bcm message is used for addressing the filter and can_id compare
               Therefore the can_id must contain the flags.
        """
        if (can_id > 0x7FF) and not (CanFlags.CAN_EFF_FLAG & can_flags):
            can_flags = can_flags | CanFlags.CAN_EFF_FLAG

        bcm = BcmMsg(opcode=BcmOpCodes.RX_READ,
                     flags=BCMFlags(0),
                     count=0,
                     interval1=0,
                     interval2=0,
                     can_id=(can_id | can_flags),
                     frames=[],
                     )
        self.send(bcm)  # send the request to read the filter

        return self.recv()  # return the bcm message with the filter content


class CanIsoTpSocket:
    """
    A socket to IsoTp. This is basically a serial connection over CAN.
    The IsoTp driver does all the work.
    """

    def __init__(self,
                 interface: str,
                 rx_addr: int,
                 tx_addr: int,
                 listen_only: bool = False,
                 use_padding: bool = False,
                 wait_tx_done: bool = False,
                 ):
        """
        :param interface: The interface name.
        :param rx_addr: The can_id for receive messages.
        :param tx_addr: The can_id for transmit messages.
        :param listen_only: Enable listen only socket option
        :param use_padding: Enable padding socket option.
        :param wait_tx_done: Enable blocking write socket option.
        """

        if tx_addr > 0x7FF:
            tx_addr = combine_can_id_and_flags(tx_addr, CanFlags.CAN_EFF_FLAG)

        if rx_addr > 0x7FF:
            rx_addr = combine_can_id_and_flags(rx_addr, CanFlags.CAN_EFF_FLAG)

        self._s = socket.socket(socket.AF_CAN, socket.SOCK_DGRAM, socket.CAN_ISOTP)
        if any([use_padding, wait_tx_done, listen_only]):
            flags = 0
            if listen_only:
                flags = flags | CAN_ISOTP_LISTEN_MODE
            if use_padding:
                # To be added to options later.
                flags = flags | CAN_ISOTP_TX_PADDING | CAN_ISOTP_RX_PADDING
            if wait_tx_done:
                flags = flags | CAN_ISOTP_WAIT_TX_DONE
            opts = IsoTpOpts(flags=flags)
            self._s.setsockopt(SOL_CAN_ISOTP, CAN_ISOTP_OPTS, opts.to_bytes())
        self._s.bind((interface, rx_addr, tx_addr))

    def __del__(self):
        self._s.close()

    def fileno(self):
        return self._s.fileno()

    def send(self, data: bytes) -> int:
        """
        A wrapper for sending data.

        :param data: The data to be sent.
        :return: The number of bytes written.
        """
        return self._s.send(data)

    def recv(self, bufsize: int = DEFAULT_BUFFER_SIZE) -> bytes:
        """
        A wrapper for receiving data.

        :param bufsize: The local buffer size to receive something from the socket, defaults to system default.
        :return: The received data.
        :raises: OSError and it's derivatives which socket class raises itself,
                 e.g. if a transfer stops before completion, this results in a TimeoutError.
        """
        return self._s.recv(bufsize)


class IsoTpOpts:
    """
    A representation of isotp options
    """

    FORMAT = "IIBccB"

    def __init__(self,
                 flags=0,
                 frame_txtime=0,
                 ext_address=0,
                 txpad_content=bytes(1),
                 rxpad_content=bytes(1),
                 rx_ext_address=0
                 ):
        """
        Constuctor

        :param flags: The flags in isotp options.
        :param frame_txtime: The time in between tx frames.
        :param ext_address: The external address if given.
        :param txpad_content: The fill byte for padding tx messages.
        :param rxpad_content: The fill byte for padding rx messages.
        :param rx_ext_address: The external address for rx if given.
        """
        self.flags = flags
        self.frame_txtime = frame_txtime
        self.ext_address = ext_address
        self.txpad_content = txpad_content
        self.rxpad_content = rxpad_content
        self.rx_ext_address = rx_ext_address

    def to_bytes(self) -> bytes:
        """
        Convert to bytes representation.

        :return: The bytes representation of the object.
        """
        opts = struct.pack(self.FORMAT,
                           self.flags,
                           self.frame_txtime,
                           self.ext_address,
                           self.txpad_content,
                           self.rxpad_content,
                           self.rx_ext_address)
        return opts

    @classmethod
    def from_bytes(cls, byte_repr: bytes):
        """
        Factory to create instance from bytes representation.

        :param byte_repr: The bytes representation of the object.
        :return: An instance of this class.
        """
        assert len(byte_repr) == cls.get_size()
        flags, frame_txtime, ext_address, txpad_content, rxpad_content, rx_ext_address = struct.unpack(cls.FORMAT,
                                                                                                       byte_repr)
        return IsoTpOpts(flags=flags,
                         frame_txtime=frame_txtime,
                         ext_address=ext_address,
                         txpad_content=txpad_content,
                         rxpad_content=rxpad_content,
                         rx_ext_address=rx_ext_address)

    @classmethod
    def get_size(cls):
        """
        Get the calculated byte size of this class.

        :return: The size in bytes.
        """
        return struct.calcsize(cls.FORMAT)

    def __eq__(self, other) -> bool:
        """
        Standard equality operation.

        :param other: Another IsoTpOpts to compare with self.
        :return: True if equal, False otherwise.
        """
        is_equal = False
        if isinstance(other, IsoTpOpts):
            is_equal = all((self.flags == other.flags,
                            self.frame_txtime == other.frame_txtime,
                            self.ext_address == other.ext_address,
                            self.txpad_content == other.txpad_content,
                            self.rxpad_content == other.rxpad_content,
                            self.rx_ext_address == other.rx_ext_address,
                            ))
        return is_equal

    def __ne__(self, other) -> bool:
        """
        Standard non equality operation

        :param other: Another IsoTpOpts to compare with self.
        :return: True if unequal, False otherwise.
        """
        return not self.__eq__(other)


class CanJ1939Name:
    pass


class CanJ1939Socket:
    """
    A socket to J1939.
    """

    def __init__(self,
                 interface: str,
                 name: Optional[int] = None,
                 pgn: Optional[int] = None,
                 source_address: Optional[int] = None,
                 enable_broadcast=True,
                 ):
        self.interface = interface

        if name is None:
            self.name = socket.J1939_NO_NAME
        else:
            self.name = name

        if pgn is None:
            self.pgn = socket.J1939_NO_PGN
        else:
            self.pgn = pgn

        if source_address is None:
            self.source_address = socket.J1939_NO_ADDR
        else:
            self.source_address = source_address

        self._s = socket.socket(socket.AF_CAN, socket.SOCK_DGRAM, socket.CAN_J1939)
        if enable_broadcast:
            self._s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self._s.bind((interface, name, pgn, source_address))

    def __del__(self):
        self._s.close()

    def fileno(self):
        return self._s.fileno()

    def sendto(self,
               pgn: int,
               data: bytes,
               addr: int,
               ) -> int:
        """
        Sent J1939 (pgn,data) tuple to a destination
        :param pgn: The program group number.
        :param data: The data.
        :param addr: The destination address
        :return: The number of bytes written.
        """
        return self._s.sendto(data, (self.interface, self.name, pgn, addr))

    def recvfrom(self, bufsize: int = DEFAULT_BUFFER_SIZE) -> dict:
        data, (interface, name, pgn, addr) = self._s.recvfrom(bufsize)
        return {"interface": interface,
                "name": name,
                "pgn": pgn,
                "addr": addr,
                "data": data}
