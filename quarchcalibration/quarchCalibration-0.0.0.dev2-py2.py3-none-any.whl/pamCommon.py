'''
Quarch Power Module Calibration Functions
Written for Python 3.6 64 bit

M Dearman April 2019
'''

'''
Calibration Flow
    Connect to PPM
    Connect to Keithley
    step through a set of values and get ADC vs Reference Value
    evaluate results vs defined limits

'''

#Imports QuarchPy library, providing the functions needed to use Quarch modules
#from quarchpy import quarchDevice #, scanDevices

## Import other libraries used in the examples
#from functools import reduce
##from quarchpy.calibration import *
import quarchpy
#from quarchpy.calibration.deviceHelpers import returnMeasurement
#import quarchpy.calibration.calibrationConfig
#import types
#from time import sleep,time
#from math import ceil
from quarchpy.calibration import *
#import threading
#from quarchpy.calibration.calibrationConfig import*
#from quarchpy.user_interface import *
#from quarchpy.user_interface import logSimpleResult,storeResult
#from quarchpy.device.device import *
#from quarchpy.device.scanDevices import userSelectDevice
#import datetime
#from quarchpy.calibration.keithley_2460_control import *
#from quarchpy.utilities.BitManipulation import *

def parseFixtureData(response,start,length):

    # split the multiline response into a list
    response = response.splitlines()
    result = ""
    # for each line
    for line in response:
        # remove 0x, swap bytes
        line = line[4:6] + line[2:4]
        # convert 4 char Hex to 16 bit binary string
        line = "{0:016b}".format(int(line,16))
        # concatenate all the strings
        result += line
    # pick out the section we want
    result = int(result[start:(start+length)],2)
    # convert two's compliment
    if (result >= 2**(length-1)):
        result -= 2**length
    return result


def getFixtureData(device,channel):
    #hold measurement
    response = device.sendCommand("read 0x0000")
    device.sendCommand("write 0x0000 " + setBit(response,3))
    #read measurement
    data = device.sendCommand("read 0x1000 to 0x1007")
    #release measurement
    response = device.sendCommand("read 0x0000")
    device.sendCommand("write 0x0000 " + clearBit(response,3))

    if (channel == "POWER_1 V"):
        return parseFixtureData(data,0,16)
    elif (channel == "POWER_1 A"):
        return parseFixtureData(data,16,25)
    elif (channel == "POWER_2 V"):
        return parseFixtureData(data,41,16)
    elif (channel == "POWER_2 A"):
        return parseFixtureData(data,57,25)

def bcdString(bcd,padding):
    # strip off "0x" if present
    if bcd[:2] == "0x":
        bcd = bcd [2:]
    # strip off leading 0's
    # loop while we have more the required minimum number of characters left
    while(len(bcd)>padding):
        # if the leading character is 0, remove it
        if bcd[0] == '0':
            bcd = bcd[1:]
        # else exit loop
        else:
            break
    return bcd


#class QTL2621 (PowerModule):

#    # Fixture Register Addresses
#    CALIBRATION_MODE_ADDR               = '0xA100'
#    CALIBRATION_CONTROL_ADDR            = '0xA101'      
#    POWER_1_VOLT_MULTIPLIER_ADDR        = '0xA105'
#    POWER_1_VOLT_OFFSET_ADDR            = '0xA106'
#    POWER_1_LOW_MULTIPLIER_ADDR         = '0xA111'
#    POWER_1_LOW_OFFSET_ADDR             = '0xA112'
#    POWER_1_LEAKAGE_MULTIPLIER_ADDR     = '0xA109'
#    POWER_2_VOLT_MULTIPLIER_ADDR        = '0xA10A'
#    POWER_2_VOLT_OFFSET_ADDR            = '0xA10B'
#    POWER_2_LOW_MULTIPLIER_ADDR         = '0xA116'
#    POWER_2_LOW_OFFSET_ADDR             = '0xA117'
#    POWER_2_LEAKAGE_MULTIPLIER_ADDR     = '0xA10E'
#    POWER_1_HIGH_MULTIPLIER_ADDR        = '0xA107'
#    POWER_1_HIGH_OFFSET_ADDR            = '0xA108'
#    POWER_2_HIGH_MULTIPLIER_ADDR        = '0xA10C'
#    POWER_2_HIGH_OFFSET_ADDR            = '0xA10D'
#    CALIBRATION_COMPLETE_ADDR	        = '0xA118'
#    HOST_VOLTAGE                        = 12000

#    # Fixture Information
#    PAMSerial = None
#    FixtureSerial = None
#    calObjectSerial = None     # The serial number of the device that is being calibrated, i.e QTL1944 in HD PPM, Fixture in PAM
#    idnStr = None
#    Firmware = None
#    Fpga = None
#    calInstrument = None
#    calInstrumentId = None
#    switchbox = None

#    # Physical Connection Tracking (what is plugged to what)
#    loadChannel = None
#    hostPowerChannel = None

#    def specific_requirements(self):

#        reportText=""

#        ## check self test
#        #if self.dut.sendCommand("*TST?") == "OK":
#        #    logSimpleResult("Self Test",True)
#        #else:
#        #    logSimpleResult("Self Test",False)
#        #    sys.exit(0)

#        # select a switchbox to use for calibration
#        if "switchbox" in calibrationResources.keys():
#            self.switchbox = calibrationResources["switchbox"]
#        self.switchbox = self.getSwitchbox()
#        self.switchboxId = self.switchbox.sendCommand("*serial?")
#        calibrationResources["switchbox"] = self.switchbox

#        # Select a Keithley SMU
#        # If no calibration instrument is provided, request it
#        while (True):
#            if (calibrationResources["loadString"] == None):
#                loadString = userSelectCalInstrument(scanFilterStr="Keithley 2460", nice=True)
#                # quit if necessary
#                if loadString == 'quit':
#                    printText("no module selected, exiting...")
#                    sys.exit(0)
#                else:
#                    calibrationResources["loadString"] = loadString
#            try:
#                # Connect to the calibration instrument
#                self.calInstrument = keithley2460(calibrationResources["loadString"])
#                # Open the connection
#                self.calInstrument.openConnection()
#                self.calInstrumentId = self.calInstrument.sendCommandQuery ("*IDN?")
#                break
#            # In fail, allow the user to try again with a new selection
#            except:
#                printText("Unable to communicate with selected instrument!")
#                printText("")
#                calibrationResources["loadString"] = None

#        # Write module specific report header to file
#        reportText += "Quarch Power Analysis Module: "
#        reportText += self.PAMSerial + "\n"
#        reportText += "Quarch Fixture: "
#        reportText += self.FixtureSerial + "\n"
#        reportText += "Quarch FW Versions: "
#        reportText += "FW:" + self.Firmware + ", FPGA: " + self.Fpga + "\n"
#        reportText += "\n"
#        reportText += "Calibration Instruments#:\n"
#        reportText += self.calInstrumentId + "\n"
#        reportText += self.switchboxId + "\n"

#        # perform uptime check and write to file
#        reportText += self.wait_for_up_time(desired_up_time=600)

#        return reportText

#    def setConnections(self,loadConnection,hostPowerConnection,reset=False):
        
#        hostPort = "a"
#        hostConnectionPortDict = {"POWER_1": "1", "POWER_2": "2"}
        
#        loadPort = "b"
#        loadConnectionPortDict = {"POWER_1": "4", "POWER_2": "5"}

#        if reset:
#            self.loadChannel = None
#            self.hostPowerChannel = None

#        # If current connections are correct
#        if self.loadChannel == loadConnection and self.hostPowerChannel == hostPowerConnection:

#            # do nothing
#            pass

#        # else connections need to change
#        else:

#            # we can't turn an individual port off (at the moment) so we turn both off first, then set anything that needs setting
#            if loadConnection == None or hostPowerConnection == None:
#                self.switchbox.sendCommand("connect off")

#            if loadConnection != None:
#                self.switchbox.sendCommand("connect " + loadPort + " " + loadConnectionPortDict[loadConnection])

#            if hostPowerConnection != None:
#                self.switchbox.sendCommand("connect " + hostPort + " " + hostConnectionPortDict[hostPowerConnection])

#        self.loadChannel = loadConnection
#        self.hostPowerChannel = hostPowerConnection

#    def open_module(self):

#        # set unit into calibration mode
#        self.dut.sendCommand("write " + QTL2621.CALIBRATION_MODE_ADDR + " 0xaa55")
#        self.dut.sendCommand("write " + QTL2621.CALIBRATION_MODE_ADDR + " 0x55aa")

#    def getSwitchbox(self):
#        # CheckSwitchbox
#        if self.switchbox is None:
#            while (True):
#                switchboxAddress = userSelectDevice(scanFilterStr=["QTL2536"], message="Select a calibration 6 Way Test Lead Switch.", nice=True)
#                if switchboxAddress == "quit":
#                    printText("User Quit Program")
#                    sys.exit(0)
#                try:
#                    self.switchbox = quarchDevice(switchboxAddress)
#                    break
#                except:
#                    printText("Unable to communicate with selected device!")
#                    printText("")
#                    switchboxAddress = None
#                    raise
#        return self.switchbox

#    def wait_for_up_time(self, desired_up_time=600):

#        returnText =""

#        try:
#            current_up_time = int(self.dut.sendCommand("conf runtime fix sec?").lower().replace("s", ""))
#            success = True
#            wait_time = desired_up_time - current_up_time
#        except:
#            success = False
#            current_up_time = 0
#            wait_time = desired_up_time
#        if current_up_time < desired_up_time:
#            skip_uptime_wait = listSelection(title="Warm Up Time", message=("The fixture uptime is " + str(current_up_time) + "s, has the fixture been powered up for more than " + str(desired_up_time) + " seconds?"),selectionList="Yes=Yes,No=No", tableHeaders=["Options"])
#            if skip_uptime_wait.lower() == "no":
#                printText("Waiting " + str(wait_time) + " seconds")
#                startTime = time.time()
#                currentTime = time.time()
#                while int(currentTime - startTime) < int(wait_time):
#                    time.sleep(0.1)
#                    progressBar(int(currentTime - startTime), (wait_time))
#                    currentTime = time.time()
#                progressBar(100,100)
#                printText("Wait Complete")
#                returnText += "Runtime check complete - Fixture temperature is stable\n"
#            else:
#                printText("Wait for runtime to reach " + str(desired_up_time) + "s skipped")
#                returnText += "Runtime check skipped - Module temperature not guaranteed to be stable.\n"

#        return returnText

#    def clear_calibration(self):

#        # set unit into calibration mode
#        self.dut.sendCommand("write " + QTL2621.CALIBRATION_MODE_ADDR + " 0xaa55")
#        self.dut.sendCommand("write " + QTL2621.CALIBRATION_MODE_ADDR + " 0x55aa")

#        # clear all calibration registers
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_OFFSET_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_MULTIPLIER_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_OFFSET_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_MULTIPLIER_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_OFFSET_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_MULTIPLIER_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_2_VOLT_OFFSET_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_2_VOLT_MULTIPLIER_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_2_LOW_OFFSET_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_2_LOW_MULTIPLIER_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_2_HIGH_OFFSET_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_2_HIGH_MULTIPLIER_ADDR + " 0x0000")
#        self.dut.sendAndVerifyCommand("write " + QTL2621.POWER_2_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
        
#        # write 0xaa55 to register to calibration complete register to tell module it is calibrated
#        self.dut.sendAndVerifyCommand("write " + QTL2621.CALIBRATION_COMPLETE_ADDR + " 0xaa55")
        
#    def write_calibration(self):

#        # write the calibration registers
#        # erase the tag memory
#        printText("Erasing TAG memory..")
#        self.dut.sendCommand("write 0xa200 0x0020")
#        # TODO: should check for completion here...
#        # wait for 2 seconds for erase to complete
#        # check busy
#        while checkBit(self.dut.sendCommand("read 0xa200"),8):
#            time.sleep(0.1)
#        # write the tag memory
#        printText("Programming TAG memory...")
#        self.dut.sendCommand("write 0xa200 0x0040")        
#        # check busy
#        while checkBit(self.dut.sendCommand("read 0xa200"),8):
#            time.sleep(0.1)

#    def close_module(self):

#        # reset the fixture FPGA
#        self.dut.sendCommand("fixture:reset")

#        #close the connection to the calibration instrument
#        self.calInstrument.closeConnection()

#    def close_all(self):

#        #close all attached devices
#        self.calInstrument.setLoadCurrent(0)
#        self.calInstrument.closeConnection()
#        self.switchbox.sendCommand("connect off")

    #class QTL2621Calibration (Calibration):

    #    def __init__(self):
    #        super().__init__()

    #    def init_cal(self,voltage):

    #        # TODO: No Power control at the moment
    #        # power up
    #        #self.powerModule.dut.sendAndVerifyCommand("power up")

    #        # set averaging to max
    #        self.powerModule.dut.sendAndVerifyCommand("rec:ave 32k")

    #        # set module into calibration mode (again?)
    #        self.powerModule.dut.sendCommand("write " + QTL2621.CALIBRATION_MODE_ADDR + " 0xaa55")   # will not verify
    #        self.powerModule.dut.sendCommand("write " + QTL2621.CALIBRATION_MODE_ADDR + " 0x55aa")   # will not verify

    #        #Reset Keithley
    #        self.powerModule.calInstrument.reset()

    #    def meas_POWER_1_volt(self):

    #        result = getFixtureData(self.powerModule.dut,"POWER_1 V")
    #        return result

    #    def meas_POWER_1_cur(self):

    #        result = getFixtureData(self.powerModule.dut,"POWER_1 A")
    #        return result

    #    def meas_POWER_2_volt(self):

    #        result = getFixtureData(self.powerModule.dut,"POWER_2 V")
    #        return result

    #    def meas_POWER_2_cur(self):

    #        result = getFixtureData(self.powerModule.dut,"POWER_2 A")
    #        return result

    #    # check connections to host power and load
    #    def checkLoadVoltage(self,voltage,tolerance):

    #        self.powerModule.calInstrument.setReferenceCurrent(0)
    #        result = self.powerModule.calInstrument.measureLoadVoltage()*1000    # *1000 because we use mV but keithley uses volts
    #        # check result is in required range
    #        if (result >= voltage-tolerance) and (result <= voltage+tolerance):
    #            return True
    #        else:
    #            return False

    #    def finish_cal(self):

    #        #turn off load
    #        self.powerModule.calInstrument.disable()

    #        #turn off switch
    #        self.powerModule.switchbox.sendCommand("connect off")

    #        # turn dut to autoranging
    #        self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.CALIBRATION_CONTROL_ADDR + " 0x00F0")

    #    def report(self,action,data):

    #        report = []

    #        # send to report file
    #        report.append("          Pass Level  +/-(" + str(self.absErrorLimit) + str(self.units) +" + " + str(self.relErrorLimit) + "%) \n")


    #        # check errors and generate report
    #        report.append('\n')

    #        if action == "calibrate":
    #           report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Raw Value ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + ' ' + '{0:>10}'.format('Pass'))
    #        elif action == "verify":
    #            report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + '   ' + '{0:>10}'.format('Pass'))

    #        report.append("==================================================================================================")

    #        # zero worst case error vars
    #        worstAbsError = 0
    #        worstRelError = 0
    #        worstRef = None
    #        overallResult = True

    #        # for each calibration reference
    #        for thisLine in data:
    #            reference = thisLine[1]
    #            ppmValue = thisLine[0]

    #            # for calibration, replace value with calibrated result
    #            if action =="calibrate":
    #                calibratedValue = self.getResult(ppmValue)
    #            # otherwise just use ppmValue directly
    #            else:
    #                calibratedValue = ppmValue

    #            # work out errors
    #            (actError,errorSign,absError,relError,result) = getError(reference,calibratedValue,self.absErrorLimit,self.relErrorLimit)

    #            # compare/replace with running worst case
    #            if absError >= worstAbsError:
    #                if relError >= worstRelError:
    #                    worstAbsError = absError
    #                    worstRelError = relError
    #                    worstCase = errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%) @ " + '{:.3f}'.format(reference) + self.units

    #            # update overall pass/fail
    #            if result != True:
    #                overallResult = False

    #            #generate report
    #            passfail = lambda x: "Pass" if x else "Fail"
    #            if action == "calibrate":
    #                report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + '{:>10.1f}'.format(calibratedValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))
    #            elif action == "verify":
    #                report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))

    #        report.append("==================================================================================================")
    #        report.append('\n')

    #        if action == "calibrate":
    #            report.append("Calculated Multiplier: " + str(self.multiplier.originalValue()) + ", Calculated Offset: " + str(self.offset.originalValue()))
    #            report.append("Stored Multiplier: " + str(self.multiplier.storedValue()) + ", Stored Offset: " + str(self.offset.storedValue()))
    #            report.append("Multiplier Register: " + self.multiplier.hexString(4) + ", Offset Register: " + self.offset.hexString(4))

    #        report.append("" + '{0:<35}'.format(self.title)+ '     '  +'{0:>10}'.format("Passed : ")+ '  '  + '{0:<5}'.format(str(overallResult))+ '     ' + '{0:>11}'.format( "worst case:")+ '  '  +'{0:>11}'.format(worstCase))
    #        report.append("\n\n\n")
            
    #        #Add to Test Summary? Do this here?
    #        passfail = lambda x: "Passed" if x else "Failed"

    #        return {"title":self.title,"result":overallResult,"worst case":worstCase,"report":('\n'.join(report))}

    class PAMVoltageCalibration (QTL2621Calibration,channelName,mulitiplierAddr,offsetAddr):

        def __init__(self,powerModule):

            self.title = channelName + " Voltage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2                  # 2mV
            self.relErrorLimit = 1                  # 1%
            self.test_min = 40                      # 40mV
            self.test_max = 14400                   # 14.4V
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 4
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("POWER_1")

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("POWER_1",None)

            # Check Host Power is present
            #while (super().checkLoadVoltage(500,500) != True):
            #    self.powerModule.setConnections("POWER_1",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_POWER_1_volt()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set POWER_1 voltage", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get POWER_1 voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2621.POWER_1_VOLT_MULTIPLIER_ADDR)
            # get POWER_1 voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2621.POWER_1_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write POWER_1 voltage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write POWER_1 voltage offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2621_POWER_1_LowCurrentCalibration (QTL2621Calibration):

        def __init__(self,powerModule):

            self.title = "POWER_1 Low Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 10                 # 10uA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 10                      # 10uA
            self.test_max = 85000                   # 85mA
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 32
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("POWER_1")

            #set manual range, full averaging, POWER_1 low current mode, POWER_2 all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.CALIBRATION_CONTROL_ADDR + " 0x00F1")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("POWER_1","POWER_1")

            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2621.HOST_VOLTAGE,1000) != True):
                self.powerModule.setConnections("POWER_1","POWER_1",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            voltage =  super().meas_POWER_1_volt()
            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_POWER_1_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set POWER_1 low current", result)
        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get POWER_1 low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2621.POWER_1_LOW_MULTIPLIER_ADDR)
            # get POWER_1 low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2621.POWER_1_LOW_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write POWER_1 low current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write POWER_1 low current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LOW_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2621_POWER_1_HighCurrentCalibration (QTL2621Calibration):

        def __init__(self,powerModule):

            self.title = "POWER_1 High Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2000               # 2mA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 1000                    # 1mA
            self.test_max = 4000000                 # 4A
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 2048
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("POWER_1")

            #set manual range, full averaging, POWER_1 high current mode, POWER_2 all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.CALIBRATION_CONTROL_ADDR + " 0x00F2")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("POWER_1","POWER_1")

            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2621.HOST_VOLTAGE,1000) != True):
                self.powerModule.setConnections("POWER_1","POWER_1",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            voltage =  super().meas_POWER_1_volt()
            #leakage = voltage*self.powerModule.calibrations["POWER_1"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["POWER_1"]["Leakage"].offset.originalValue()
            return load_meas_cur(self.powerModule.calInstrument)# + leakage

        def readVal(self):

            return super().meas_POWER_1_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set POWER_1 high current", result)

            # once we've completed low and high current we can set leakage on the fixture
            #result = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_LEAKAGE_MULTIPLIER_ADDR + " " + self.powerModule.calibrations["POWER_1"]["Leakage"].multiplier.hexString(4))

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get POWER_1 high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2621.POWER_1_HIGH_MULTIPLIER_ADDR)
            # get POWER_1 high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2621.POWER_1_HIGH_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write POWER_1 high current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write POWER_1 high current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2621.POWER_1_HIGH_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2621_POWER_2_VoltageVerification (QTL2621Calibration):

        def __init__(self,powerModule):

            self.title = "POWER_2 Voltage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2mV
            self.relErrorLimit = 1      # 1%
            self.test_min = 40          # 40mV
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("POWER_2")

            self.powerModule.setConnections("POWER_2",None)

            # Check Host Power is present
            #while (super().checkLoadVoltage(500,500) != True):
                #self.powerModule.setConnections("POWER_2",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_POWER_2_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2621_POWER_2_LowCurrentVerification (QTL2621Calibration):

        def __init__(self,powerModule):

            self.title = "POWER_2 Low Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 10     # 10uA
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 100         # 100uA
            self.test_max = 1000        # 1mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("POWER_2")

            self.powerModule.setConnections("POWER_2","POWER_2")

            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2621.HOST_VOLTAGE,1000) != True):
                self.powerModule.setConnections("POWER_2","POWER_2",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_POWER_2_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2621_POWER_2_HighCurrentVerification (QTL2621Calibration):

        def __init__(self,powerModule):

            self.title = "POWER_2 High Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2000       # 2mA
            self.relErrorLimit = 1          # 1% tolerance
            self.test_min = 1000            # 1mA
            self.test_max = 4000000         # 4A
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("POWER_2")

            self.powerModule.setConnections("POWER_2","POWER_2")

            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2621.HOST_VOLTAGE,1000) != True):
                self.powerModule.setConnections("POWER_2","POWER_2",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_POWER_2_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    def __init__(self,dut):

        # set the name of this module
        self.name = "PCIe x16 Power Measurement Fixture"
        self.dut = dut
        
        # Serial numbers (ensure QTL at start)
        self.enclosureSerial = self.dut.sendCommand("*ENCLOSURE?")
        if (self.enclosureSerial.find ("QTL") == -1):
            self.enclosureSerial = "QTL" + self.enclosureSerial
        # fetch the enclosure position
        self.enclosurePosition = self.dut.sendCommand("*POSITION?")
        self.PAMSerial = self.dut.sendCommand ("*SERIAL?")
        if (self.PAMSerial.find ("QTL") == -1):
            self.PAMSerial = "QTL" + self.PAMSerial
        # Fixture Serial
        # fixture serial is retrieved as BCD, we need to convert and pad it
        self.FixtureSerial = "QTL" + bcdString(dut.sendCommand("read 0xA102"),4) + "-" + bcdString(dut.sendCommand("read 0xA103"),2) + "-" + bcdString(dut.sendCommand("read 0xA104"),3) # TODO: this should be replaced with fix:serial? command when implemented
        # calObjectSerial Serial
        self.calObjectSerial = self.FixtureSerial
        # Filename String
        self.filenameString = self.FixtureSerial
        # Code version (FPGA)
        self.idnStr = dut.sendCommand ("*IDN?")
        pos = self.idnStr.upper().find ("FPGA 1:")
        if (pos != -1):
            versionStr = self.idnStr[pos+7:]
            pos = versionStr.find ("\n")
            if (pos != -1):
                versionStr = versionStr[:pos].strip()
            else:
                pass
        else:
            versionStr = "NOT-FOUND"    
        self.Fpga = versionStr.strip()
    
        # Code version (FW)    
        pos = self.idnStr.upper().find ("PROCESSOR:")
        if (pos != -1):
            versionStr = self.idnStr[pos+10:]
            pos = versionStr.find ("\n")
            if (pos != -1):
                versionStr = versionStr[:pos].strip()            
            else:
                pass
        else:
            versionStr = "NOT-FOUND"    
        self.Firmware = versionStr.strip()

        self.calibrations = {}
        # populate POWER_1 channel with calibrations
        self.calibrations["POWER_1"] = {
            "Voltage":self.QTL2621_POWER_1_VoltageCalibration(self),
            #"Leakage":self.QTL2621_POWER_1_LeakageCalibration(self),
            "Low Current":self.QTL2621_POWER_1_LowCurrentCalibration(self),
            "High Current":self.QTL2621_POWER_1_HighCurrentCalibration(self)
            }
        # populate POWER_2 channel with calibrations
        self.calibrations["POWER_2"] = {
            "Voltage":self.QTL2621_POWER_2_VoltageCalibration(self),
            #"Leakage":self.QTL2621_POWER_2_LeakageCalibration(self),
            "Low Current":self.QTL2621_POWER_2_LowCurrentCalibration(self),
            "High Current":self.QTL2621_POWER_2_HighCurrentCalibration(self)
            }

        self.verifications = {}
        # populate POWER_1 channel with verifications
        self.verifications["POWER_1"] = {
            "Voltage":self.QTL2621_POWER_1_VoltageVerification(self),
            "Low Current":self.QTL2621_POWER_1_LowCurrentVerification(self),
            "High Current":self.QTL2621_POWER_1_HighCurrentVerification(self)
            }
        # populate POWER_2 channel with verifications
        self.verifications["POWER_2"] = {
            "Voltage":self.QTL2621_POWER_2_VoltageVerification(self),
            "Low Current":self.QTL2621_POWER_2_LowCurrentVerification(self),
            "High Current":self.QTL2621_POWER_2_HighCurrentVerification(self)
            }

if __name__== "__main__":
    main()

