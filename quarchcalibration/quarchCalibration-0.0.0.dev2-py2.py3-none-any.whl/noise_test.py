"""
Date: 12/02/2021
Author: Stuart Boon
Version: 1.0

Noise Test
"""
import sys
# Import QPS functions
from quarchpy import qpsInterface, isQpsRunning, startLocalQps, GetQpsModuleSelection, quarchDevice, quarchQPS,qps, requiredQuarchpyVersion
# OS allows us access to path data
from quarchpy.user_interface import *
import os, time
import datetime
from user_interface.user_interface import get_check_valid_calPath
from quarchpy.debug.SystemTest import get_quarchpy_version
import argparse
# TestCenter functions
from quarchpy.utilities import TestCenter

current_milli_time = lambda: int(round(time.time() * 1000))

def test_main(module_address=None, voltage_limit=50, current_limit=250, channel_list=None, file_path="", close_QPS=False):
    testName = "Test1"
    if channel_list == None:
        raise ValueError("\"channel_list\" must not be none. Example could be:  [\"12v\",\"5v\"]")

    file_path = get_check_valid_calPath(file_path)

    # If we're in testcenter setup the test
    if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
        # Set up database logging
        TestCenter.setup("Quarch_Internal", "Internal", "Login=-", "Password=-")



    # Checks if QPS is running on the localhost
    if isQpsRunning() == False:
        # Start QPS from quarchpy
        startLocalQps(args="-ccs")



    myQps = qpsInterface()
    if module_address == None:
        module_address = GetQpsModuleSelection (myQps)
    myQuarchDevice = quarchDevice(module_address, ConType="QPS")
    myQpsDevice = quarchQPS(myQuarchDevice)
    myQpsDevice.openConnection()

    DUTserialNumber = myQpsDevice.sendCommand("*serial?")
    module_set_up(myQpsDevice, DUTserialNumber)
    if ('1944' in DUTserialNumber):

        DUTserialNumber = myQpsDevice.sendCommand("*enclosure?")
    elif ('2098' in DUTserialNumber):
        DUTserialNumber = myQpsDevice.sendCommand("fix serial?")[3:]

    # Prints out connected module information
    printText("Running QPS Automation Example")
    printText("Module Name:")
    printText(myQpsDevice.sendCommand("hello?"))

    # get TestTime
    test_time = datetime.datetime.now()
    # open report for writing and write system header
    fileName = file_path + "\\" +"QTL"+DUTserialNumber+"_"+test_time.strftime("%d-%m-%y_%H-%M") + "-noise_test.txt"

    printText("")
    printText("Report file: " + fileName)
    reportFile = open(fileName, "a+", encoding='utf-8')
    reportFile.write("\n")
    reportFile.write("Quarch Technology Noise Test Report\n")
    reportFile.write("\n")
    reportFile.write("---------------------------------\n")
    reportFile.write("\n")
    reportFile.write("System Information:\n")
    reportFile.write("\n")
    try:
        reportFile.write("QuarchPy Version: " + get_quarchpy_version() + "\n")
    except:

        reportFile.write("QuarchPy Version: unknown\n")
    reportFile.write("Noise Test Time: " + str(test_time.replace(microsecond=0)) + "\n")
    reportFile.write("\n")
    reportFile.write("---------------------------------\n")
    reportFile.write("\n")
    reportFile.flush()

    myQpsDevice.sendCommand("RECord:AVEraging 4")


    # Set the averaging rate for the module.  This sets the resolution of data to record
    # This is done via a direct command to the power module
    setupPowerOutput(myQpsDevice)

    # Start a stream, using the local folder of the script and a time-stamp file name in this example
    fileName = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    myStream = myQpsDevice.startStream(file_path + fileName)

    start_stream_time = current_milli_time()
    start_test_time=current_milli_time()
    time_since_start=start_test_time - start_stream_time
    myStream.addAnnotation('Start '+testName, "e"+str(1))
    time.sleep(0.5)
    myQpsDevice.sendCommand("Sig:12v:Volt 0") # sb db debug TODO move this HD specific
    time.sleep(1.5)
    end_test_time = current_milli_time()
    myStream.addAnnotation('End Test'+testName, "e"+str(2))

    time.sleep(1) # lets it stream for 1 seconds
    myStream.stopStream()
    myStream.hideAllDefaultChannels()
    time.sleep(8) #let the module unload the buffer


    myStats = myStream.get_stats()
    myTest = myStats.loc[myStats['Text', "NA"] == "Start "+testName]
    voltageTestDict = {}
    currentTestDict = {}

    # Get the required values for test.
    if "3.3v" in channel_list: #3.3v channel name for QTL1999 and other
        max_voltage_3v3 = myTest.at[0, ('voltage 3.3V Max', 'mV')]
        max_current_3v3 = myTest.at[0, ('current 3.3V Max', 'uA')]
        voltageTestDict["max_voltage_3.3V"] = max_voltage_3v3
        currentTestDict["max_current_3.3V"] = max_current_3v3

    if "3v3" in channel_list: #3.3v channel name for QTL2347
        max_voltage_3v3 = myTest.at[0, ('voltage 3V3 Max', 'mV')]
        max_current_3v3 = myTest.at[0, ('current 3V3 Max', 'uA')]
        voltageTestDict["max_voltage_3V3"] = max_voltage_3v3
        currentTestDict["max_current_3vV"] = max_current_3v3

    if "12v" in channel_list:
        max_voltage_12v = myTest.at[0, ('voltage 12V Max', 'mV')]
        max_current_12v = myTest.at[0, ('current 12V Max', 'uA')]
        voltageTestDict["max_voltage_12v"] = max_voltage_12v
        currentTestDict["max_current_12v"] = max_current_12v

    if "3.3v aux" in channel_list:
        max_voltage_3v3_aux = myTest.at[0, ("voltage 3.3V Aux Max", 'mV')]
        max_current_3v3_aux = myTest.at[0, ("current 3.3V Aux Max", 'uA')]
        voltageTestDict["max_voltage_3.3V_aux"] = max_voltage_3v3_aux
        currentTestDict["max_current_3.3V_aux"] = max_current_3v3_aux

    if "5v" in channel_list:
        max_voltage_5v = myTest.at[0, ('voltage 5V Max', 'mV')]
        max_current_5v = myTest.at[0, ('current 5V Max', 'uA')]
        voltageTestDict["max_voltage_5v"] = max_voltage_5v
        currentTestDict["max_current_5v"] = max_current_5v



    #voltageTestDict = {"max_voltage_3v3":max_voltage_3v3, "max_voltage_3v3_aux":max_voltage_3v3_aux, "max_voltage_12v":max_voltage_12v}
    #currentTestDict = {"max_current_3v3": max_current_3v3, "max_current_3v3_aux": max_current_3v3_aux, "max_current_12v": max_current_12v}

    test_overview=[] # used to write to the report file and
    all_tests_passed=True
    for k,v in voltageTestDict.items():
        if int(v) > voltage_limit:
            result = "FAIL"
            passed = False
            all_tests_passed=False
            time.sleep(0.1)
        else:
            result = "PASS"
            passed = True
            time.sleep(0.1)

        logSimpleResult(k, passed)
        test_overview.append((k, result, v, voltage_limit))

    for k,v in currentTestDict.items():
        if int(v) > current_limit:
            result = "FAIL"
            passed = False
            all_tests_passed=False
            time.sleep(0.1)
        else:
            result = "PASS"
            passed = True
            time.sleep(0.1)

        logSimpleResult(k, passed)
        test_overview.append((k, result, v, current_limit))

    printToConsole = True if(User_interface.instance.selectedInterface == "console") else False
    resultsTable = displayTable(tableData=test_overview, tableHeaders=("Test Name", "Result", "Value", "Limit"), printToConsole=printToConsole)

    reportFile.write(resultsTable)
    reportFile.flush()
    reportFile.close()

    #Comment this out if you don't want to view recordings of failed tests
    if all_tests_passed == False: close_QPS =False

    if close_QPS == False:
        showDialog(title="Quit QPS?", message="Continue when you are you ready to close QPS.")
        close_QPS=True
    if close_QPS:
        qps.closeQps()

    return test_overview


def module_set_up(myQpsDevice, DUTserialNumber):

    if DUTserialNumber.__contains__("1944"):
        myQpsDevice.sendCommand("sig 12v voltage 0")
        myQpsDevice.sendCommand("sig 5v voltage 0")
        myQpsDevice.sendCommand("conf out mode 5v") #will fail if smart module plugged in
        myQpsDevice.sendCommand("run pow up")
        return
    elif DUTserialNumber.__contains__("2098"):
        return



def main(argstring):
    # Handle expected command line arguments here using a flexible parsing system
    parser = argparse.ArgumentParser(description='Noise Test parameters')
    parser.add_argument('-m', '--module', help='IP Address or netBIOS name of the DUT', type=str.lower)
    parser.add_argument('-p', '--path', help='Path to store the report file', type=str.lower)
    parser.add_argument('-v', '--voltage_limit', help='The max voltage that would allow a test pass in mV', type=float)
    parser.add_argument('-c', '--current_limit', help='The max current that would allow a test pass in mA', type=float)
    parser.add_argument('--channel_list', action='append', help='A list of the channel names to be tested', type=str.lower)
    parser.add_argument('--close_qps', help="True if you don't QPS to stay open to view the stream after the test has finished", type=str.lower)
    parser.add_argument('-l', '--logging', help='Level of logging to report', choices=['warning', 'error', 'debug'], type=str.lower,default='warning')
    parser.add_argument('-u', '--userMode',  help=argparse.SUPPRESS,choices=['console','testcenter'], type=str.lower,default='console') #Passes the output to testcenter instead of the console Internal Use
    args, extra_args = parser.parse_known_args(argstring)

    # Create a user interface object
    thisInterface = User_interface(args.userMode)

    #
    if args.close_qps is not None:
        args.close_qps = str2bool(args.close_qps)

    # Call the main noise test, passing the provided arguments
    return test_main(module_address=args.module, voltage_limit=args.voltage_limit, current_limit=args.current_limit, channel_list=args.channel_list, file_path=args.path, close_QPS=args.close_qps)
    #return test_main(module_address="USB::QTL2312-01-015", voltage_limit=50, current_limit=250,channel_list=["3v3", "3v3 aux", "12v"])


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__ == "__main__":
    main (sys.argv[1:])
    #main(["-h"])
    #main (["-mUSB::QTL2312-01-015", "-pQ:\\Production\\Calibration\\pythoncals\\NoiseTests", "-v50", "-c250","--channel_list",  "3v3", "--channel_list", "3v3 aux", "--channel_list", "12v", "-uconsole", "--close_qps", "False"])


    #PAM FIXTURE
    #main(["-v50", "-c250","--channel_list", "3.3v", "--channel_list", "3.3v aux", "--channel_list", "12v", "-uconsole", "--close_qps","True"])
    #HDPPM
    #main(["-v3.3333", "-c3000","--channel_list", "5v","--channel_list", "12v", "-uconsole", "--close_qps","True"])

