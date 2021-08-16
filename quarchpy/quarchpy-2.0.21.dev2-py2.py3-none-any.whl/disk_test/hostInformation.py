'''
Implements a cross platform system for scanning and querying system resources.

########### VERSION HISTORY ###########

06/05/2019 - Andy Norrie    - First version

####################################
'''

import logging
import platform as pt
import os
from sys import platform
import sys
import time

from quarchpy.disk_test.dtsComms import DTSCommms
from quarchpy.disk_test.dtsGlobals import dtsGlobals
from quarchpy.user_interface import *
from quarchpy.disk_test.SmartCTLController import UniversalSmartCtl
from quarchpy.disk_test.Drive_wrapper import DriveWrapper
from quarchpy.device.scanDevices import listDevices

# from quarchpy.disk_test.driveTestCore import notifyChoiceOption, sendMsgToGUI, checkChoiceResponse, setChoiceResponse

# to make input function back compatible with Python 2.x
if hasattr(__builtins__, 'raw_input'):
    input = raw_input

# defining this here means we will never have to differentiate
if platform == "win32":
    from quarchpy.disk_test.lspci import WindowsLSPCI as lspci
    from quarchpy.disk_test.sasFuncs import WindowsSAS as sasDET


else:
    from quarchpy.disk_test.lspci import LinuxLSPCI as lspci
    from quarchpy.disk_test.sasFuncs import LinuxSAS as sasDET


class HostInformation:
    # creating new (private) class instance
    __mylspci = lspci()
    __mySAS = sasDET()
    __mySmartCtl = UniversalSmartCtl()
    internalResults = {}

    def __init__(self):
        self.comms = DTSCommms()
        self.device_list = []

    '''
    Lists physical drives on the system, returning them in the form "{drive-type:identifier=drive description}"
    '''



    def return_wrapped_drives(self, drive_type=None):
        """
        Returns a list of all drives found on the system
        The drives are all contained in "DriveWrapper" objects

        :param drive_type: STR : Can be used to specify the type of drive.
                                 Leave as None will return all
                    Accepted Values : [ 'lspci', '*', 'smart' ]
        :return: List : DriveWrapper objects
        """
        # moving directory incase using lspci exe for Windows.
        cwd = os.getcwd()
        os.chdir(os.path.dirname(__file__))

        dev_list = []

        # returns devices wrapped in DeviceWrapper.
        if not drive_type:
            dev_list = self.__mySmartCtl.wrap_smartctl_devices()
            dev_list += self.__mylspci.wrap_lspci_devices()
            dev_list += self.__mySAS.wrap_sas_devices()
        elif drive_type.lower() == "lspci":
            dev_list = self.__mylspci.wrap_lspci_devices()
        elif drive_type.lower() == "smart":
            dev_list = self.__mySmartCtl.wrap_smartctl_devices()
        else:
            dev_list = self.__mySAS.wrap_sas_devices()

        # returning back to the original directory
        os.chdir(cwd)

        if not dev_list:
            logging.debug("ERROR - No devices found to display")

        return dev_list

    def is_wrapped_device_present(self, wrapped_device):

        if not isinstance(wrapped_device, DriveWrapper):
            logging.error("Passed a not drive_wrapper object for device present check")
            return False

        # get a list of wrapped drives
        device_list = self.return_wrapped_drives()

        for item in device_list:
            # Double check as switches may have same identifier but different description.
            if wrapped_device.identifier_str == item.identifier_str and wrapped_device.description == item.description:
                return True

        return False

    def verify_wrapped_drive_link(self, wrapped_drive, expected_link=None):

        """
        find drive passed and returns boolean if Link speed is same as expected value passed
        LSPCI devices only

        :param wrapped_drive: DriveWrapper
        :param expected_link: Expected speed (e.g '16 GT/s')
        :return: True if maintained else False
        """

        if not isinstance(wrapped_drive, DriveWrapper):
            logging.error("Passed a not drive_wrapper object for device link speed check")
            return False

        # Cannot CURRENTLY (2.0.20) verify a none lspci device link speed / lane width
        if not "lspci" in str(wrapped_drive.system_cmd).lower():
            logging.debug("Cannot currently verify a NONE lspci device")
            return True

        device_list = self.return_wrapped_drives()

        for item in device_list:
            if wrapped_drive.identifier_str == item.identifier_str and wrapped_drive.description == item.description:
                if expected_link == item.link_speed:
                    return True

        return False

    def return_wrapped_drive_link(self, wrapped_drive):
        """
        Finds drive passed and returns it's current link speed
        LSPCI devices only

        :param wrapped_drive: DriveWrapper
        :return: Link speed value if found else ""
        """
        if not isinstance(wrapped_drive, DriveWrapper):
            logging.error("Passed a not drive_wrapper object for device lane width check")
            return ""

        device_list = self.return_wrapped_drives()

        for item in device_list:
            if wrapped_drive.identifier_str == item.identifier_str and wrapped_drive.description == item.description:
                return item.link_speed

        return ""

    def verify_wrapped_drive_width(self, wrapped_drive, expected_width=None):
        """
        find drive passed and returns boolean if lane width is same as expected value passed
        LSPCI devices only

        :param wrapped_drive: DriveWrapper
        :param expected_width: Expected width (e.g 'x2')
        :return: True if maintained else False
        """
        if not isinstance(wrapped_drive, DriveWrapper):
            logging.error("Passed a not drive_wrapper object for device lane width check")
            return False

        # Cannot CURRENTLY (2.0.20) verify a none lspci device link speed / lane width
        if not "lspci" in str(wrapped_drive.system_cmd).lower():
            logging.debug("Cannot currently verify a NONE lspci device")
            return True

        device_list = self.return_wrapped_drives()

        for item in device_list:
            if wrapped_drive.identifier_str == item.identifier_str and wrapped_drive.description == item.description:
                if expected_width == item.lane_width:
                    return True

        return False

    def return_wrapped_drive_width(self, wrapped_drive):
        """
        Find drive passed and return it's current reported lane width
        LSPCI devices only

        :param wrapped_drive: DriveWrapper
        :return: Lane width if found else ""
        """

        if not isinstance(wrapped_drive, DriveWrapper):
            logging.error("Passed a not drive_wrapper object for device lane width check")
            return ""

        device_list = self.return_wrapped_drives()

        for item in device_list:
            if wrapped_drive.identifier_str == item.identifier_str and wrapped_drive.description == item.description:
                return item.lane_width

        return ""

    def get_wrapped_drive_from_choice(self, selection):
        """
        Returns DriveWrapper object based on identifying string passed in parameter

        :param selection: STR
                         # selection passed is the identifier for the drive.
                         # Smartctl  : /dev/sda
                         # lspci     : 04:00.0
                         # WMIC      :
                         # LSSCSI    :
        :return: DriveWrapper if device was found, else None
        """
        device_list = self.return_wrapped_drives()


        for item in device_list:
            if item.identifier_str == str(selection).strip():
                return item

        logging.error("Could not find drive from item passed")
        return None








    def store_initial_drive_stats(self, drive, mapping_mode=False):
        if str(drive.drive_type).lower() == "pcie":
            self.internalResults[drive.identifier_str + "_linkSpeed"], self.internalResults[
                drive.identifier_str + "_linkWidth"] = self.__mylspci.getPcieLinkStatus(drive.identifier_str, mapping_mode)


    def display_drives(self):
        """
        Function used only in the Quarchpy.run file
        Used to display all found drives on the system to current terminal output

        :return: N/A
        """
        drives = self.return_wrapped_drives()

        drive_dict = {}
        for drive in drives:
            drive_dict[drive.identifier_str] = "({2} - {1}) {0}".format(drive.description, drive.drive_type,
                                                                       drive.system_cmd)

        listDevices(drive_dict)
