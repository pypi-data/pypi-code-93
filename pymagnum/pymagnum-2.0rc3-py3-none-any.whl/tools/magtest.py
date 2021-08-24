#
# Copyright (c) 2018-2020 Charles Godwin <magnum@godwin.ca>
#
# SPDX-License-Identifier:    BSD-3-Clause
#
#  This module tests the functonality of the serial interface
#  by attempting to read 50 packets of data and parsing them
#  The results are dumped to the terminal
#
import argparse
import time
import traceback
import os 
import sys

from magnum.magnum import Magnum
from magnum import __version__

class Logger(object):
    def __init__(self, logname=None):
        self.terminal=sys.stdout
        if logname:
            self.log=open(logname, 'w')
        else:
            self.log = None

    def write(self, message):
        self.terminal.write(message)
        if self.log:
            self.log.write(message)

    def flush(self):
        if self.log and not self.log.closed:
            self.log.flush()

    def close(self):
        if self.log:
            self.log.close()


def main():
    global args
    parser = argparse.ArgumentParser(
        description="Magnum RS485 Reader Test", fromfile_prefix_chars='@', prog="Magnum Test", epilog="Use `python -m serial.tools.list_ports` to identify devices.")
    parser.add_argument("-d", "--device", default="/dev/ttyUSB0",
                        help="Serial device name (default: %(default)s)")
    group = parser.add_argument_group("seldom used arguments")
    group.add_argument("-n", "--packets", default=50, type=int,
                    help="Number of packets to generate (default: %(default)s)")
    group.add_argument("-t", "--timeout", default=0.001, type=float,
                    help="Timeout for serial read - float between 0 and 1 second (default: %(default)s)")
    group.add_argument("-nc", "--nocleanup", action="store_true",
                    help="Suppress clean up of unknown packets (default: %(default)s)", dest='cleanpackets')
    group.add_argument("--trace", action="store_true", default=False,
                        help="Add most recent raw packet info to data (default: %(default)s)")
    group.add_argument("--log",action="store_true", default=False,
                        help="Log test to logfile in current directory (default: %(default)s)")                       
    args = parser.parse_args()
    if args.timeout < 0 or args.timeout > 1.0:
        parser.error(
            "argument -t/--timeout: must be a number (float) between 0 and 1 second. i.e. 0.005")
    if args.packets < 1:
        parser.error("argument -n/--packets: must be greater than 0.")
    args.cleanpackets = not args.cleanpackets
    print('Version:{0}'.format(__version__))
    print("Options:{}".format(str(args).replace("Namespace(", "").replace(")", "")))
    if args.log:
        logfile = os.path.join(os.getcwd(), "magtest_" + time.strftime("%Y-%m-%d_%H%M%S") + ".txt")
        sys.stdout = Logger(logname=logfile)
    try:
        reader = Magnum(device=args.device, packets=args.packets, trace=args.trace,
                            timeout=args.timeout, cleanpackets=args.cleanpackets)
    except:
        print("Error detected attempting to open serial device")
        traceback.print_exc()
        exit(2)
    try:
        start = time.time()
        packets = reader.getPackets()
        duration = time.time() - start
        unknown = 0
        formatstring = "Length:{0:2} {1:10}=>{2}"
        device_list = dict()
        for item in [Magnum.INVERTER, Magnum.REMOTE, Magnum.RTR, Magnum.BMK, Magnum.AGS, Magnum.PT100, Magnum.ACLD]:
            device_list[item] = 'NA'
        device_list[Magnum.RTR] = False
        for packet in packets:
            if packet[0] == Magnum.UNKNOWN:
                unknown += 1
            if args.trace:
                end = ' decode:'
            else:
                end = '\n'
            print(formatstring.format(len(packet[1]), packet[0], packet[1].hex().upper()), end=end)
            if args.trace:
                print(*packet[2], end = ' ')
                print(packet[3])
            packetType = packet[0]
            if packetType in (Magnum.INV, Magnum.INV_C):
                device_list[Magnum.INVERTER]  = True
            elif packetType in (Magnum.REMOTE_C,
                                Magnum.REMOTE_00):
                device_list[Magnum.REMOTE]  = True
            elif packetType == Magnum.REMOTE_11:
                pass #ignored
            elif packetType == Magnum.REMOTE_80:
                device_list[Magnum.REMOTE]  = True
                if device_list[Magnum.BMK]  != True:
                    device_list[Magnum.BMK]  = False
            elif packetType in (
                                Magnum.REMOTE_A0,
                                Magnum.REMOTE_A1,
                                Magnum.REMOTE_A2,
                                Magnum.REMOTE_A3,
                                Magnum.REMOTE_A4):
                device_list[Magnum.REMOTE]  = True
                if device_list[Magnum.AGS]  != True:
                    device_list[Magnum.AGS]  = False
            elif packetType in (
                                Magnum.REMOTE_C0,
                                Magnum.REMOTE_C1,
                                Magnum.REMOTE_C2,
                                Magnum.REMOTE_C3,
                                Magnum.REMOTE_C4,
                                ):
                device_list[Magnum.REMOTE]  = True
                if device_list[Magnum.PT100]  != True:
                    device_list[Magnum.MagnumPT100]  = False            
            elif packetType == Magnum.REMOTE_D0:
                device_list[Magnum.REMOTE]  = True
                if device_list[Magnum.ACLD]  != True:
                        device_list[Magnum.ACLD]  = False  
            elif packetType == Magnum.BMK_81:
                device_list[Magnum.BMK]  = True 
            elif packetType in (Magnum.AGS_A1, Magnum.AGS_A2):
                device_list[Magnum.AGS]  = True 
            elif packetType == Magnum.RTR_91:
                device_list[Magnum.RTR]  = True 
            elif packetType in (Magnum.PT_C1, Magnum.PT_C2, Magnum.PT_C3):
                device_list[Magnum.PT100]  = True       
            elif packetType == Magnum.ACLD_D1:
                device_list[Magnum.ACLD]  = True        
            
        format1 = "Packets:{0} of {1} with {2} UNKNOWN, in {3:2.2f} seconds"
        format2 = "Packets:{0} in {3:2.2f} seconds"
        format = format1 if unknown > 0 else format2
        print(format.format(len(packets), args.packets, unknown, duration))
    # Analyze packets
        if len(packets) > unknown:
            for key, value in device_list.items():
                if value == 'NA':
                    print ("{0} not supported".format(key))
                elif value == False:
                    print ("{0} not connected".format(key))
                else:
                    print("{0} Detected".format(key))
            if device_list[Magnum.PT100] == True:
                print ("{0} has limited support, contact the author.".format(magnum.PT100))
            if device_list[Magnum.ACLD] == True:
                print ("{0} is not currently supported, contact the author.".format(magnum.ACLD))
            if args.log:
                print("Output was logged to {}".format(logfile))

    except:
        print("Error detected attempting to read network data - test failed")
        traceback.print_exc()
        exit(2)

if __name__ == '__main__':
    main()
