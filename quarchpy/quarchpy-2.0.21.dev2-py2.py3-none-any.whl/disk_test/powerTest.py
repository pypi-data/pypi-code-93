import os
import sys
import time
import logging
from quarchpy.user_interface import*
from connection_specific.connection_QPS import QpsInterface
from quarchpy.disk_test.dtsGlobals import dtsGlobals
from quarchpy.disk_test import driveTestConfig
from quarchpy.disk_test.driveTestCore import sendLogMessage, executeAndCheckCommand
from quarchpy.device.quarchQPS import quarchStream



'''
Function to run a set number of hotplug remove/insert cycles using a simple staged hot-plug and added pin-bounce
A single pin bounce pattern can be specified and applied to any number of signal(s)/group(s).  The bounce pattern is
applied to source 4, as this is not used by default on any existing module.


quarchName=Name of Quarch module (resource item name)
driveName=Name of drive under test (resource item name)
insertTime=Hot-plug time step (per pin length) in mS
bouncePattern=Simple|25mS|10mS|500uS|50% (Type|delay|length|period|duty cycle)
bounceSignals=Name1|Name2|Name3
repeats=Number of times to repeat each point in the sweep
onTime=Optional time in seconds to wait for drive enumeration
offTime=Optional time in seconds to wait for drive removal
bounceOnPlug=Optional flag, should bounce be applied to plug
bounceOnPull=Optional flag, should bounce be applied to pull (defaults to False)
'''


def SetupStreamAveraging(quarchDevice, averagingRate):
    quarchDevice.sendCommand("record:averaging " + str(averagingRate))


def simplePowerMarginingTest(uniqueID, quarchName, driveName, maxDecreasePercent, numberOfIncrements, repeats=1,
                            onTime=15, offTime=10, averagingRate="16k"):
    startTestTime = time.time()
    errorSubCounter = 0
    # time to wait after the device has been found
    customSleepEnd = 5

    # Stop doing math at 100x required
    maxDecreasePercent = float(maxDecreasePercent) / 100

    logging.info("\nStarting test point " + str(uniqueID))

    # Create a counter to increment id's
    counter = 0
    startUID = uniqueID
    repeating = (int(repeats) > 1)

    # Validate required callbacks
    if ("TEST_GETDISKSTATUS" not in driveTestConfig.testCallbacks):
        raise ValueError("You have not implemented the required TEST_GETDISKSTATUS callback!")

    if ("TEST_GETRESOURCE" not in driveTestConfig.testCallbacks):
        raise ValueError("You have not implemented the required TEST_GETRESOURCE callback!")

    # Log start of test
    sendLogMessage(time.time(), "testDescription",
                   "Starting Power Margining test, over " + str(
                       repeats) + " repetitions", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name,
                   uId=uniqueID);

    # Get the resource for the named Quarch module
    quarchDevice = driveTestConfig.testCallbacks["TEST_GETRESOURCE"](quarchName)
    if (quarchDevice is None):
        raise ValueError("Selected test resource: [" + quarchName + "] not found")

    # Get the resource for the named disk drive under test
    driveObject = driveTestConfig.testCallbacks["TEST_GETRESOURCE"](driveName)
    if (driveObject is None):
        raise ValueError("Selected test resource: [" + driveName + "] not found")

    # Setup Averaging
    SetupStreamAveraging(quarchDevice, averagingRate)
    # Begin Stream
    filePath = os.path.dirname(os.path.realpath(__file__))
    fileName = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    time.sleep(3)
    myStream = quarchDevice.startStream(filePath + fileName)

    # Requires a change to ensure the power isn't set too high for whatever device we're using
    powerSetting = 12000
    currentPower = powerSetting
    # Finding 'power threshold'
    minimumPower = int(powerSetting) - (int(powerSetting) * int(maxDecreasePercent))
    # Finding decrement size
    powerDecrement = (float(powerSetting) * float(maxDecreasePercent)) / float(numberOfIncrements)
    logging.info(powerDecrement)
    # Send message to say starting power margin test

    for loop in range(0, int(numberOfIncrements) + 1):

        # sig:12v:volt 11800
        # sig:12v:volt?
        counter = 0
        # Check to see if user requested end of test
        if dtsGlobals.continueTest is False:
            printText("Test Aborted, waiting on next test start..")
            myStream.addAnnotation('TEST ABORTED')
            return

        currentPower = int(currentPower) - int(powerDecrement)

        logging.info("current power = " + str(currentPower))

        if (loop == 0):
            currentPower = powerSetting

        uniqueID = startUID + "." + str(int(loop + 1))
        sendLogMessage(time.time(), "testDescription", "Power Margining cycle " + str(int(loop + 1)) +
                       "; " + str(currentPower) + "mV",
                       os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId=uniqueID)


        executeAndCheckCommand(quarchDevice, "run:power down")
        time.sleep(0.1)
        myStream.addAnnotation("Starting Power Margining cycle " + str(int(loop + 1)) + "\\n" + str(currentPower) + "mV")
        # TESTING for not being detected
        driveTestConfig.testCallbacks["TEST_NEWSLEEP"](driveObject, 0, offTime)

        counter = counter + 1

        # Verify the device is gone
        if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](uniqueID, driveObject, 0)):
            sendLogMessage(time.time(), "testResult",
                           "HOT_PLUG: Drive removed within " + str(offTime) + "seconds, as expected",
                           os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult": True},
                           uId=uniqueID + "." + str(counter));
        else:
            sendLogMessage(time.time(), "testResult",
                           "HOT_PLUG: Drive NOT removed as expected after " + str(offTime) + "seconds",
                           os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult": False},
                           uId=uniqueID + "." + str(counter));
            errorSubCounter += 1


        executeAndCheckCommand(quarchDevice, "sig:12v:volt " + str(currentPower))

        # Plug the module
        executeAndCheckCommand(quarchDevice, "run:power up")

        # TESTING for detection
        driveTestConfig.testCallbacks["TEST_NEWSLEEP"](driveObject, 1, onTime)

        counter = counter + 1

        # Verify the device is present
        if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](uniqueID, driveObject, 1)):
            sendLogMessage(time.time(), "testResult",
                           "HOT_PLUG: Drive detected as expected after " + str(onTime) + "seconds",
                           os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult": True},
                           uId=uniqueID + "." + str(counter));
            elapsedTime = time.time() - startTestTime
            myStream.addAnnotation("Drive Found\\n" + str(round(elapsedTime,5)) + "s")

        else:
            sendLogMessage(time.time(), "testResult", "HOT_PLUG: Drive NOT detected after " + str(onTime) + "seconds",
                           os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult": False},
                           uId=uniqueID + "." + str(counter));
            errorSubCounter += 1

        time.sleep(customSleepEnd)

    myStream.stopStream()

    uniqueID = startUID + "." + str(int(numberOfIncrements) + 2)
    sendLogMessage(time.time(), "testDescription", "Results of Power Margining test", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId=uniqueID)

    # Track errors from this time step
    if errorSubCounter == 0:
        sendLogMessage(time.time(), "testResult", "Power Margining test passed all repetitions",
                       os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult": True},
                       uId=uniqueID + ".1");
    else:
        sendLogMessage(time.time(), "testResult",
                       "Power Margining test failed: " + str(errorSubCounter) + " sub-test points",
                       os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult": False},
                       uId=uniqueID + ".1");

    elapsedTime = time.time() - startTestTime
    summaryString = "Total TestTime Elapsed: " + str(int(elapsedTime)) + "s, Error count = " + str(errorSubCounter)

    sendLogMessage(time.time(), "testSummary", summaryString,
                   os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId=uniqueID + ".2")

    logging.info("Test point end")

    # closing the opened connection to QPS
    quarchDevice.closeConnection()

