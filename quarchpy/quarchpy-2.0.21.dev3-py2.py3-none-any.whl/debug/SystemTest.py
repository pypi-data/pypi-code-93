from quarchpy import *
from quarchpy.device import *
import pkg_resources
from pkg_resources import parse_version, get_distribution
import os
import platform
import time
import sys
import subprocess
from quarchpy._version import __version__
# TODO: Move this code to a seperate system_test function so it can be called from other places.  Only argument handling should be done in main
def main (args=None):
    """
    Main function to allow the system test to be called direct from the command line
    """

    print("")
    print("SYSTEM INFORMATION")
    print("------------------")
    print("OS Name: " + os.name)
    print("Platform System: " + platform.system())
    print("Platform: " + platform.platform())
    if "nt" in os.name: print ("Platform Architecture: " + platform.architecture()[0])
    print("Platform Release:  " + platform.release())

    try:
        print("Quarchpy Version: " + get_quarchpy_version())
    except:
        print("Unable to detect Quarchpy version")
    try:
        print("Quarchpy Location: " + pkg_resources.get_distribution("quarchpy").location)
    except:
        print("Unable to detect Quarchpy location")

    try:
        print("Python Version: " + sys.version)
    except:
        print("Unable to detect Python version")

    try:
        print("QIS version number: " + get_QIS_version())
    except:
        print("Unable to detect QIS version")

    try:
        javaVersion = bytes(subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)).decode()
        print("Java Version: "+ str(javaVersion))
    except:
        print("Unable to detect java version"
              "If Java is not installed then QIS and QPS will NOT run")
    try:
        javaLocation = get_java_location()
        print("Java Location: "+ str(javaLocation))
    except:
        print("Unable to detect java location"
              "If Java is not installed then QIS and QPS will NOT run")


	
	# Scan for all quarch devices on the system
    print("")
    print("DEVICE COMMUNICATION TEST")
    print("-------------------------")
    print("")
    deviceList = scanDevices('all', favouriteOnly=False)
    print("Devices visible:\r\n" +str(deviceList))
    print("")
    moduleStr = userSelectDevice(deviceList, nice=True, additionalOptions = ["Rescan","Quit", "All Conn Types"])
    if moduleStr == "quit":
        return 0
    print("Selected module is: "+moduleStr)
    # Create a device using the module connection string
    myDevice = quarchDevice(moduleStr)
    QuarchSimpleIdentify(myDevice)

    # Close the module before exiting the script
    myDevice.closeConnection()



def QuarchSimpleIdentify(device1):
    """
    Prints basic identification test data on the specified module, compatible with all Quarch devices

    Parameters
    ----------
    device1: quarchDevice
        Open connection to a quarch device
        
    """
    # Print the module name
    print("MODULE IDENTIFY TEST")
    print("--------------------")
    print("")
    print("Module Name: "),
    print(device1.sendCommand("hello?"))
    print("")
    # Print the module identify and version information
    print("Module Identity Information: ")
    print(device1.sendCommand("*idn?"))




def get_QIS_version():
    """
    Returns the version of QIS.  This is the version of QIS currenty running on the local system if one exists.
    Otherwise the local version within quarchpy will be exectued and its version returned.

    Returns
    -------
    version: str
        String representation of the QIS version number
        
    """

    qis_version = ""
    my_close_qis = False
    if isQpsRunning() == False:
        my_close_qis = True
        startLocalQis(headless=True)
        
    myQis = qisInterface()
    qis_version = myQis.sendAndReceiveCmd(cmd="$version")
    if "No Target Device Specified" in qis_version:
        qis_version = myQis.sendAndReceiveCmd(cmd="$help").split("\r\n")[0]
    if my_close_qis:
        myQis.sendAndReceiveCmd(cmd = "$shutdown")
    return qis_version


def get_java_location():
    """
    Returns the location of java.

    Returns
    -------
    location: str
        String representation of the java location.
    """
    if "windows" in platform.platform().lower():
        location = bytes(subprocess.check_output(['where', 'java'], stderr=subprocess.STDOUT)).decode()
    elif "linux" in platform.platform().lower():
        location = bytes(subprocess.check_output(['whereis', 'java'], stderr=subprocess.STDOUT)).decode()
    else:
        location = "Unable to detect OS to check java version."
    return location

def get_quarchpy_version():
    try:
       return __version__
    except:
        return "Unknown"


if __name__ == "__main__":
    main()