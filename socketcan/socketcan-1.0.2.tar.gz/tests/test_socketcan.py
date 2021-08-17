""" Test_socketcan

    Collection of tests for socketcan module to be run with pytest / tox / coverage
    @author: Patrick Menschel (menschel.p@posteo.de)
    @license: GPL v3
"""
import datetime
from random import randint, randbytes
from typing import Optional

import select
import pytest

from queue import Queue, Empty

from socketcan import CanFrame, CanFlags, CanFdFlags, CanFdFrame, BCMFlags, BcmMsg, BcmOpCodes, CanRawSocket, \
    CanIsoTpSocket, CanBcmSocket, CanJ1939Socket

from socketcan.socketcan import split_can_id_and_flags, IsoTpOpts, CAN_ISOTP_TX_PADDING, CAN_ISOTP_RX_PADDING

from subprocess import CalledProcessError, check_output

from threading import Thread

import time

import platform

from tests.mocks import MockSocket

import logging

LOGGER = logging.getLogger()


def is_can_available() -> Optional[list]:
    """
    get available can interfaces via ip link
    :return: A list of interface names that are family link/can
    """
    try:
        return [line.split(":")[1].strip() for line in
                check_output("ip -o link show | grep link/can", shell=True).decode().splitlines()]
    except CalledProcessError:
        pass
    return


@pytest.fixture
def can_interface() -> Optional[str]:
    """
    PyTest fixture to be used in socket based tests.
    It basically retrieves the network interface
    names for can and then selects the first one.
    :return:
    """
    interface_names = is_can_available()
    if interface_names:
        return interface_names[0]


def mcp0_and_mcp1_available() -> bool:
    """
    Determine if mcp0 and mcp1 are available,
    assuming both are directly connected for real transfer.
    :return: True if both available.
    """
    ret = False
    available_can_interfaces = is_can_available()
    if available_can_interfaces is not None and all(
            interface in available_can_interfaces for interface in ["mcp0", "mcp1"]):
        ret = True
    return ret


def vcan0_available() -> bool:
    """
    Determine if vcan0 is available.
    :return: True if both available.
    """
    ret = False
    available_can_interfaces = is_can_available()
    if available_can_interfaces is not None and "vcan0" in available_can_interfaces:
        ret = True
    return ret


def is_isotp_available() -> bool:
    """
    A helper function to determine if isotp
    is available on the system.
    :return: True if the driver module file is found.
    """
    try:
        if check_output("ls /lib/modules/$(uname -r)/kernel/net/can/can-isotp.ko", shell=True).strip():
            return True
    except CalledProcessError:
        pass
    return False


def is_j1939_available() -> bool:
    """
    A helper function to determine if isotp
    is available on the system.
    :return: True if the driver module file is found.
    """
    try:
        if check_output("ls /lib/modules/$(uname -r)/kernel/net/can/j1939/can-j1939.ko", shell=True).strip():
            return True
    except CalledProcessError:
        pass
    return False


def receive_from_can_isotp_socket(interface, rx_addr, tx_addr, bufsize, use_padding, listen_only, q):
    """
    A helper function to receive something via isotp and verify the contents in a test.
    This is intended to be run in a thread parallel to the test.
    :param interface: The interface name.
    :param rx_addr: The rx can id.
    :param tx_addr: The tx can id.
    :param bufsize: The buffer size to be used.
    :param use_padding: The padding option flag.
    :param listen_only: The listen_only_option_flag
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanIsoTpSocket(interface=interface, rx_addr=rx_addr, tx_addr=tx_addr,
                       use_padding=use_padding, listen_only=listen_only)
    q.put(s.recv(bufsize=bufsize))


def receive_from_can_raw_socket(interface, q):
    """
    A helper function to receive a can frame from raw socket.
    :param interface: The interface name.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanRawSocket(interface=interface)
    q.put(s.recv())


def receive_from_bcm_socket(interface, can_id, interval, q):
    """
    A helper function to receive a can frame from bcm socket.
    :param interface: The interface name.
    :param can_id: The can id to be received.
    :param interval: The expected interval or rather the timeout.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanBcmSocket(interface=interface)
    data = bytes.fromhex("FF FF FF FF FF FF FF FF")
    frame = CanFrame(can_id=can_id,
                     data=data)

    s.setup_receive_filter(frame=frame, timeout=interval * 2)
    q.put(s.recv())


def receive_from_j1939_socket(interface, q):
    """
    A helper function to receive a can frame from j1939 socket.
    :param interface: The interface name.
    :param q: The queue where to put the received data into.
    :return: None.
    """
    s = CanJ1939Socket(interface=interface)
    q.put(s.recvfrom())


# def generate_random_can_frame() -> CanFrame:
#     can_id = randint(1, 0x1FFFFFFF)
#     data_len = randint(0, 8)
#     data = randbytes(data_len)
#     frame = CanFrame(can_id=can_id, data=data)
#     return frame
#
#
# class RandomFrameGenerator:
#     """
#     An object that generates CanFrames
#     sends these can frames on a given CAN interface
#     and puts them into a queue, so the parent application
#     can check every frame is received via interface.
#     Note: This is actually an enhanced version of cangen command.
#     """
#
#     def __init__(self,
#                  interface: str,
#                  q: Optional[Queue] = None,
#                  wait_time: Optional[float] = None,
#                  number_of_frames: Optional[int] = None,
#                  ):
#         """
#         Constructor
#         :param interface: The CAN interface.
#         :param q: The queue to put the sent frames.
#         """
#         self.interface = interface
#         self.q = q
#         self.wait_time = wait_time
#         self.timeout = 1
#         self.number_of_frames = number_of_frames
#         self.s = CanRawSocket(interface=interface)
#         self.worker = Thread(target=self.generate_frames)
#         self.worker.setDaemon(True)
#         self.worker.start()
#
#     def generate_frames(self) -> None:
#         """
#         Worker thread to generate frames.
#         :return: None.
#         """
#         len_of_can_frame = CanFrame.get_size()
#         while self.number_of_frames is None \
#                 or self.number_of_frames > 0:
#             try:
#                 ready_to_send = select.select([], [self.s, ], [], self.timeout)[1]
#             except select.error:
#                 pass
#             else:
#                 if ready_to_send:
#                     frame = generate_random_can_frame()
#                     if ready_to_send[0].send(frame) == len_of_can_frame:
#                         if self.q is not None:
#                             self.q.put(frame)
#                         if self.wait_time is not None:
#                             time.sleep(self.wait_time)
#                         if self.number_of_frames is not None:
#                             self.number_of_frames = self.number_of_frames - 1


class TestObjectCreation:
    """
    A collection of tests for concat / parse objects.
    """

    def test_unequal_frames(self):
        can_id1 = 0x123
        data1 = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id1,
                          data=data1)

        can_id2 = 0x12345678
        data2 = bytes(range(0, 0x44, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        assert frame1 != frame2

    def test_can_frame_creation_with_short_id(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_short_id_and_short_data(self):
        can_id = 0x123
        data = bytes(range(0, 0x44, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_short_id_and_rtr_flag(self):
        can_id = 0x123
        flags = CanFlags.CAN_RTR_FLAG
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          flags=flags,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_short_id_and_err_flag(self):
        can_id = 0x123
        flags = CanFlags.CAN_ERR_FLAG
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          flags=flags,
                          data=data)
        flags = frame1.flags
        assert not (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_long_id_and_no_eff_flag(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_long_id_and_eff_flag(self):
        can_id = 0x12345678
        flags = CanFlags.CAN_EFF_FLAG
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          flags=flags,
                          data=data)
        flags = frame1.flags
        assert (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_frame_creation_with_long_id_and_short_data(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x44, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        flags = frame1.flags
        assert (flags & CanFlags.CAN_EFF_FLAG)
        assert not (flags & CanFlags.CAN_RTR_FLAG)
        assert not (flags & CanFlags.CAN_ERR_FLAG)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFrame.get_size()

        frame2 = CanFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_fd_frame_creation(self):
        can_id = 0x12345678
        data = bytes(range(64))
        frame1 = CanFdFrame(can_id=can_id,
                            data=data)
        frame_as_bytes = frame1.to_bytes()

        assert len(frame_as_bytes) == CanFdFrame.get_size()

        frame2 = CanFdFrame.from_bytes(frame_as_bytes)
        assert frame1 == frame2

    def test_can_fd_frame_unequal(self):
        can_id = 0x12345678
        data = bytes(range(64))
        frame1 = CanFdFrame(can_id=can_id,
                            data=data)
        can_id = 0x123
        data = bytes(range(64))
        frame2 = CanFdFrame(can_id=can_id,
                            data=data)
        assert frame1 != frame2

    def test_bcm_msg_creation(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        opcode = BcmOpCodes.TX_SETUP
        flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1, ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_unequal_bcm_msgs(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        opcode = BcmOpCodes.TX_SETUP
        flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1, ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        interval2 = 1
        bcm2 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval2,
                      can_id=can_id,
                      frames=frames,
                      )

        assert bcm1 != bcm2

    def test_bcm_msg_creation_with_2_frames(self):
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        can_id2 = 0x456
        data2 = bytes(range(0, 0x88, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        opcode = BcmOpCodes.TX_SETUP
        flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1,
                  frame2,
                  ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_bcm_msg_creation_with_2_extended_frames_and_different_sizes(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        can_id2 = 0x1FFFF456
        data2 = bytes(range(0, 0x44, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        opcode = BcmOpCodes.TX_SETUP
        flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1,
                  frame2,
                  ]
        interval = 0.1
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=0,
                      interval2=interval,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_bcm_msg_creation_with_2_extended_frames_and_ival1(self):
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))

        frame1 = CanFrame(can_id=can_id,
                          data=data)
        can_id2 = 0x1FFFF456
        data2 = bytes(range(0, 0x44, 0x11))
        frame2 = CanFrame(can_id=can_id2,
                          data=data2)

        opcode = BcmOpCodes.TX_SETUP
        flags = (BCMFlags.SETTIMER | BCMFlags.STARTTIMER)
        frames = [frame1,
                  frame2,
                  ]
        interval1 = 0.1
        interval2 = 5
        bcm1 = BcmMsg(opcode=opcode,
                      flags=flags,
                      count=0,
                      interval1=interval1,
                      interval2=interval2,
                      can_id=can_id,
                      frames=frames,
                      )
        bcm_as_bytes = bcm1.to_bytes()
        assert len(bcm_as_bytes) == BcmMsg.get_size() + (CanFrame.get_size() * len(frames))

        bcm2 = BcmMsg.from_bytes(bcm_as_bytes)
        assert bcm1 == bcm2

    def test_isotp_opts(self):
        opts = IsoTpOpts(flags=CAN_ISOTP_TX_PADDING | CAN_ISOTP_RX_PADDING,
                         frame_txtime=100,
                         ext_address=0xF1,
                         txpad_content=b"\xAA",
                         rxpad_content=b"\xCC",
                         rx_ext_address=0xFA
                         )
        data = opts.to_bytes()
        opts2 = IsoTpOpts.from_bytes(data)
        assert opts == opts2
        assert not opts != opts2

    @pytest.mark.xfail
    def test_isotp_opts_should_fail(self):
        opts = IsoTpOpts(flags=CAN_ISOTP_TX_PADDING | CAN_ISOTP_RX_PADDING,
                         frame_txtime=100,
                         ext_address=0xF1,
                         txpad_content=b"\xAA",
                         rxpad_content=b"\xCC",
                         rx_ext_address=0xFA
                         )
        data = opts.to_bytes()
        opts.ext_address = 0
        opts2 = IsoTpOpts.from_bytes(data)
        assert opts == opts2


@pytest.mark.skipif(not is_can_available(), reason="this test requires a can interface to be set up")
class TestCanRawSocket:
    """
    A collection of tests for the raw socket.
    """

    def test_can_raw_socket(self, can_interface):
        s = CanRawSocket(interface=can_interface)
        fileno = s.fileno()
        assert fileno
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()

        assert frame1 == frame2

        assert not frame1 != frame2  # this is stupid but what do we do for 100% coverage ;-)

    def test_can_raw_socket_w_can_fd(self, can_interface):
        s = CanRawSocket(interface=can_interface)
        can_id = 0x12345678
        data = bytes(range(64))
        frame1 = CanFdFrame(can_id=can_id,
                            data=data)

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()
        print(frame2.can_id)
        print(frame2.data)
        assert frame1 == frame2

    @pytest.mark.skipif(not vcan0_available(),
                        reason="this test requires vcan0")
    def test_can_type_after_vcan_transfer(self):
        s = CanRawSocket(interface="vcan0")
        can_id = 0x12345678
        data = bytes(range(8))  # this frame could be a normal can frame
        frame1 = CanFdFrame(can_id=can_id,
                            data=data,
                            fd_flags=CanFdFlags(0))

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=("vcan0", q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()
        print(frame2.can_id)
        print(frame2.data)
        assert frame1 == frame2

    @pytest.mark.skipif(not mcp0_and_mcp1_available(),
                        reason="this test requires two connected interfaces, mcp0 and mcp1")
    def test_can_type_after_real_transfer(self):
        s = CanRawSocket(interface="mcp0")
        can_id = 0x12345678
        data = bytes(range(8))  # this frame could be a normal can frame
        frame1 = CanFdFrame(can_id=can_id,
                            data=data,
                            fd_flags=CanFdFlags(0))

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=("mcp1", q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.send(frame1)
        frame2 = q.get(timeout=10)
        p.join()
        print(frame2.can_id)
        print(frame2.data)
        assert frame1 == frame2


@pytest.mark.skipif(not (is_can_available()
                         and is_isotp_available()),
                    reason="this test requires a can interface to be set up and isotp kernel module, mainline kernel "
                           ">= 5.10")
class TestCanIsoTpSocket:
    """
    A collection of tests for the IsoTp socket.
    """

    def test_can_isotp_socket(self, can_interface):
        rx_addr = 0x7e0
        tx_addr = 0x7e8
        use_padding = False
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        fileno = s.fileno()
        assert fileno
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2

    def test_can_isotp_socket_with_extended_ids(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = False
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2

    def test_can_isotp_socket_with_extended_ids_and_listenonly(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = False
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, q,))
        p.setDaemon(True)
        p.start()

        q2 = Queue()
        p2 = Thread(target=receive_from_can_isotp_socket,
                    args=(can_interface, tx_addr, rx_addr, bufsize, False, True, q2,))
        p2.setDaemon(True)
        p2.start()

        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()
        data3 = q2.get(timeout=10)
        p2.join()

        assert data == data2 == data3

    def test_can_isotp_socket_with_extended_ids_and_padding(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        use_padding = True
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, use_padding=use_padding)
        data = bytes(range(64))
        bufsize = len(data)
        q = Queue()
        # Note: the receive thread logically has rx_addr, tx_addr inverted!
        p = Thread(target=receive_from_can_isotp_socket,
                   args=(can_interface, tx_addr, rx_addr, bufsize, use_padding, False, q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.send(data)

        data2 = q.get(timeout=10)
        p.join()

        assert data == data2

    def test_should_fail_missing_flow_control_on_transfer(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr)
        data = bytes(range(64))
        with pytest.raises(OSError):
            err = s.send(data)

    def test_should_fail_missing_flow_control_on_transfer_and_wait_tx(self, can_interface):
        rx_addr = 0x18DA01FA
        tx_addr = 0x18DAFA01
        s = CanIsoTpSocket(interface=can_interface, rx_addr=rx_addr, tx_addr=tx_addr, wait_tx_done=True)
        data = bytes(range(64))
        with pytest.raises(OSError):
            err = s.send(data)


@pytest.mark.skipif(not is_can_available(), reason="this test requires a can interface to be set up")
class TestCanBcmSocket:
    """
    A collection of tests for the BCM socket.
    """

    def test_bcm_msg_and_bcm_socket_send_operation(self, can_interface):
        s = CanBcmSocket(interface=can_interface)
        fileno = s.fileno()
        assert fileno
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)
        opcode = BcmOpCodes.TX_SETUP
        flags = BCMFlags.SETTIMER | BCMFlags.STARTTIMER
        interval = 1
        frames = [frame1, ]
        bcm = BcmMsg(opcode=opcode,
                     flags=flags,
                     count=0,
                     interval1=0,
                     interval2=interval,
                     can_id=can_id,
                     frames=frames,
                     )
        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.setDaemon(True)
        p.start()
        try:
            s.send(bcm)
        except OSError:
            assert False, "The length of bcm message is false. Length {0} Platform {1}".format(len(bcm.to_bytes()),
                                                                                               platform.machine())
        else:
            time.sleep(1)
            frame2 = q.get(timeout=10)
            p.join()

            assert frame1 == frame2

    def test_setup_cyclic_message_via_bcm(self, can_interface):
        interval = 0.5
        s = CanBcmSocket(interface=can_interface)
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame = CanFrame(can_id=can_id,
                         data=data)

        s.setup_cyclic_transmit(frame=frame, interval=interval)

    def test_setup_receive_filter_and_read_filter_via_bcm(self, can_interface):
        interval = 0.5
        s = CanBcmSocket(interface=can_interface)
        can_id = 0x12345678
        data = bytes(range(0, 0x88, 0x11))
        frame = CanFrame(can_id=can_id,
                         data=data)

        s.setup_receive_filter(frame=frame, timeout=interval)

        # we do it wrong to trigger auto adding CAN_EFF_FLAG
        can_id = 0x12345678
        bcm = s.get_receive_filter(can_id=can_id)

        assert bcm.opcode == BcmOpCodes.RX_STATUS
        assert frame.can_id | frame.flags == bcm.can_id
        assert len(bcm.frames) == 1
        frame2 = bcm.frames[0]
        assert frame == frame2

    def test_should_fail_defect_recv_from_can_bcm_socket(self, can_interface):
        # create a cyclic message
        bcm_sock = CanBcmSocket(interface=can_interface)
        bcm_sock._s = MockSocket()
        assert bcm_sock.recv() is None

    def test_should_fail_defect_recv_from_can_raw_socket(self, can_interface):
        # create a raw message
        raw_sock = CanRawSocket(interface=can_interface)
        raw_sock._s = MockSocket()
        assert raw_sock.recv() is None

    def test_bcm_and_bcm_socket_receive_message_short_can_id(self, can_interface):
        # create a cyclic message
        interval = 0.5
        s1 = CanBcmSocket(interface=can_interface)
        can_id = 0x123
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)

        q = Queue()
        p = Thread(target=receive_from_bcm_socket, args=(can_interface, can_id, interval, q))
        p.setDaemon(True)

        s1.setup_cyclic_transmit(frame=frame1, interval=interval)
        p.start()

        rx_bcm = q.get(timeout=interval * 10)
        p.join()

        print("Received message from BCM")
        print("can_id {0:X} opcode {1} flags {2} nframes {3}".format(rx_bcm.can_id, rx_bcm.opcode, rx_bcm.flags,
                                                                     len(rx_bcm.frames)))
        if rx_bcm.frames:
            print("BCM message included a CAN Frame {0:X} {1} {2}".format(rx_bcm.frames[0].can_id,
                                                                          rx_bcm.frames[0].flags,
                                                                          rx_bcm.frames[0].data.hex()))
        assert rx_bcm.opcode == BcmOpCodes.RX_CHANGED
        assert frame1.can_id, frame1.flags == split_can_id_and_flags(rx_bcm.can_id)
        assert len(rx_bcm.frames) == 1
        frame2 = rx_bcm.frames[0]
        assert frame1 == frame2

    def test_bcm_and_bcm_socket_receive_message_long_can_id(self, can_interface):
        # create a cyclic message
        interval = 0.5
        s1 = CanBcmSocket(interface=can_interface)
        can_id = 0x123456FF
        data = bytes(range(0, 0x88, 0x11))
        frame1 = CanFrame(can_id=can_id,
                          data=data)

        q = Queue()
        p = Thread(target=receive_from_bcm_socket, args=(can_interface, can_id, interval, q))
        p.setDaemon(True)

        s1.setup_cyclic_transmit(frame=frame1, interval=interval)
        p.start()

        rx_bcm = q.get(timeout=interval * 10)
        p.join()

        print("Received message from BCM")
        print("can_id {0:X} opcode {1} flags {2} nframes {3}".format(rx_bcm.can_id, rx_bcm.opcode, rx_bcm.flags,
                                                                     len(rx_bcm.frames)))
        if rx_bcm.frames:
            print("BCM message included a CAN Frame {0:X} {1} {2}".format(rx_bcm.frames[0].can_id,
                                                                          rx_bcm.frames[0].flags,
                                                                          rx_bcm.frames[0].data.hex()))

        assert rx_bcm.opcode == BcmOpCodes.RX_CHANGED
        assert frame1.can_id, frame1.flags == split_can_id_and_flags(rx_bcm.can_id)
        assert len(rx_bcm.frames) == 1
        frame2 = rx_bcm.frames[0]
        assert frame1 == frame2


@pytest.mark.skipif(not (is_can_available()
                         and is_j1939_available()),
                    reason="this test requires a can interface to be set up and j1939 kernel module, mainline kernel "
                           ">= 5.4")
class TestCanJ1939Socket:
    """
    A collection of tests for the j1939 socket.
    """

    def test_can_j1939_socket(self, can_interface):
        source_address = 0x20
        s = CanJ1939Socket(interface=can_interface, source_address=source_address)
        fileno = s.fileno()
        assert fileno
        data = bytes(range(8))
        pgn = 0xFECA
        dest = 0xFF

        q = Queue()
        p = Thread(target=receive_from_can_raw_socket, args=(can_interface, q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.sendto(pgn=pgn, data=data, addr=dest)
        frame = q.get(timeout=10)
        p.join()

        assert frame.data == data
        assert frame.can_id == source_address + (pgn << 8) + (0x18 << 24)

    def test_can_j1939_recvfrom(self, can_interface):
        source_address = 0x20
        s = CanJ1939Socket(interface=can_interface, source_address=source_address)
        data = bytes(range(8))
        pgn = 0xFECA
        dest = 0xFF

        q = Queue()
        p = Thread(target=receive_from_j1939_socket, args=(can_interface, q,))
        p.setDaemon(True)
        p.start()
        time.sleep(1)
        s.sendto(pgn=pgn, data=data, addr=dest)
        j1939_dict = q.get(timeout=10)
        p.join()
        LOGGER.info("{0}".format(j1939_dict))
        assert j1939_dict.get("data") == data
        assert j1939_dict.get("pgn") == pgn

# @pytest.mark.long
# @pytest.mark.skipif(not is_can_available(), reason="this test requires a can interface to be set up")
# class TestPerformance:
#
#     @pytest.mark.skipif(not vcan0_available(),
#                         reason="this test requires vcan0")
#     def test_data_rate_via_can_raw_socket(self):
#         interface = "vcan0"
#         framecount = 0
#         duration = datetime.timedelta(minutes=2)
#         timeout = datetime.datetime.now() + duration
#         q = Queue()
#         s = CanRawSocket(interface=interface)
#         framegen = RandomFrameGenerator(interface=interface,
#                                         q=q,
#                                         # wait_time=0.001,
#                                         )
#         while current_time := datetime.datetime.now() < timeout:
#             next_frame = s.recv()
#             queued_frame = q.get()
#             assert next_frame == queued_frame
#             framecount = framecount + 1
#
#         LOGGER.info("{0} frames in {1}".format(framecount, duration))
#
#     @pytest.mark.skipif(not mcp0_and_mcp1_available(),
#                         reason="this test requires two connected interfaces, mcp0 and mcp1")
#     @pytest.mark.timeout(3610)
#     def test_data_rate_via_can_raw_socket_on_real_interface(self):
#         interface = "mcp0"
#         interface2 = "mcp1"
#         framecount = 0
#         dropped_frames_on_interface = 0
#         duration = datetime.timedelta(minutes=60)
#         timeout = datetime.datetime.now() + duration
#         q = Queue()
#         s = CanRawSocket(interface=interface)
#         framegen = RandomFrameGenerator(interface=interface2,
#                                         q=q,
#                                         # wait_time=0.001,
#                                         )
#         while current_time := datetime.datetime.now() < timeout:
#             next_frame = s.recv()  # blocking until a frame arrives
#             try:
#                 queued_frame = q.get(timeout=0.001)
#             except Empty:
#                 continue
#             else:
#                 if next_frame != queued_frame:
#                     cnt = 0
#                     while next_frame != queued_frame:
#                         try:
#                             queued_frame = q.get(timeout=0.001)
#                         except Empty:
#                             break
#                         else:
#                             cnt = cnt + 1
#                     dropped_frames_on_interface = dropped_frames_on_interface + cnt
#                     LOGGER.error(
#                         "Re-synced queue after {0} dropped frames (overall {1})".format(cnt, dropped_frames_on_interface))
#                 framecount = framecount + 1
#
#         LOGGER.info("{0} frames in {1} (dropped frames by interface {2})".format(framecount, duration,
#                                                                                  dropped_frames_on_interface))
