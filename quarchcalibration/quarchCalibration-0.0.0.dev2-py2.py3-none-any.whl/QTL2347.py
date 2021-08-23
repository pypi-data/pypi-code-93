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

# Import other libraries used in the examples
from functools import reduce
#from quarchpy.calibration import *
import quarchpy
from quarchpy.calibration.deviceHelpers import returnMeasurement
import quarchpy.calibration.calibrationConfig
import types
from time import sleep,time
from math import ceil
from quarchpy.calibration.PowerModuleCalibration import *
import threading
from quarchpy.calibration.calibrationConfig import*
from quarchpy.user_interface import *
from quarchpy.user_interface import logSimpleResult,storeResult
from quarchpy.device.device import *
from quarchpy.device.scanDevices import userSelectDevice
import datetime
from quarchpy.calibration.keithley_2460_control import *
from quarchpy.utilities.BitManipulation import *

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

    if (channel == "3V3 VOLT"):
        return parseFixtureData(data,0,16)
    elif (channel == "3V3 CUR"):
        return parseFixtureData(data,16,25)
    elif (channel == "12V VOLT"):
        return parseFixtureData(data,41,16)
    elif (channel == "12V CUR"):
        return parseFixtureData(data,57,25)
    elif (channel == "3V3_AUX VOLT"):
        return parseFixtureData(data,82,16)
    elif (channel == "3V3_AUX CUR"):
        return parseFixtureData(data,98,20)

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


class QTL2347 (PowerModule):

    # Fixture Register Addresses
    CALIBRATION_MODE_ADDR               = '0xA100'
    CALIBRATION_CONTROL_ADDR            = '0xA101'      
    V3_3_LOW_MULTIPLIER_ADDR            = '0xA105'
    V3_3_LOW_OFFSET_ADDR                = '0xA106'
    V3_3_HIGH_MULTIPLIER_ADDR           = '0xA107'
    V3_3_HIGH_OFFSET_ADDR               = '0xA108'
    V3_3_VOLT_MULTIPLIER_ADDR           = '0xA109'
    V3_3_VOLT_OFFSET_ADDR               = '0xA10A'
    V3_3_LEAKAGE_MULTIPLIER_ADDR        = '0xA10B'
    V12_LOW_MULTIPLIER_ADDR             = '0xA10C'
    V12_LOW_OFFSET_ADDR                 = '0xA10D'
    V12_HIGH_MULTIPLIER_ADDR            = '0xA10E'
    V12_HIGH_OFFSET_ADDR                = '0xA10F'
    V12_VOLT_MULTIPLIER_ADDR            = '0xA110'
    V12_VOLT_OFFSET_ADDR                = '0xA111'
    V12_LEAKAGE_MULTIPLIER_ADDR         = '0xA112'
    V3_3_AUX_MULTIPLIER_ADDR            = '0xA113'
    V3_3_AUX_OFFSET_ADDR                = '0xA114'
    V3_3_AUX_VOLT_MULTIPLIER_ADDR       = '0xA115'
    V3_3_AUX_VOLT_OFFSET_ADDR           = '0xA116'
    V3_3_AUX_LEAKAGE_MULTIPLIER_ADDR    = '0xA117'
    CALIBRATION_COMPLETE_ADDR	        = '0xA118'
    LOAD_VOLTAGE                        = 12000

    # Fixture Information
    PAMSerial = None
    FixtureSerial = None
    calObjectSerial = None     # The serial number of the device that is being calibrated, i.e QTL1944 in HD PPM, Fixture in PAM
    idnStr = None
    Firmware = None
    Fpga = None
    calInstrument = None
    calInstrumentId = None
    switchbox = None

    # Physical Connection Tracking (what is plugged to what)
    loadChannel = None
    hostPowerChannel = None

    # defigning the connection
    hostPort = "A"
    loadPort = "B"
    hostConnectionPortDict = {"12V": "1", "3V3": "2", "3V3_AUX": "3"}
    loadConnectionPortDict = {"12V": "4", "3V3": "5", "3V3_AUX": "6"}

    # general
    waitComplete = False
    checkedWiering = False

    def specific_requirements(self):
        reportText=""

        # select a switchbox to use for calibration
        if "switchbox" in calibrationResources.keys():
            self.switchbox = calibrationResources["switchbox"]
        self.switchbox = self.getSwitchbox()
        calibrationResources["switchbox"] = self.switchbox

        if self.checkedWiering != True:
            self.checkWiring()
            self.checkedWiering = True

        # Select a Keithley SMU
        # If no calibration instrument is provided, request it
        while (True):
            if (calibrationResources["loadString"] == None):
                loadString = userSelectCalInstrument(scanFilterStr="Keithley 2460", nice=True)
                # quit if necessary
                if loadString == 'quit':
                    printText("no module selected, exiting...")
                    sys.exit(0)
                else:
                    calibrationResources["loadString"] = loadString
            try:
                # Connect to the calibration instrument
                self.calInstrument = keithley2460(calibrationResources["loadString"])
                # Open the connection
                self.calInstrument.openConnection()
                self.calInstrumentId = self.calInstrument.sendCommandQuery ("*IDN?")
                break
            # In fail, allow the user to try again with a new selection
            except:
                printText("Unable to communicate with selected instrument!")
                printText("")
                calibrationResources["loadString"] = None

        # Write module specific report header to file
        reportText += "Quarch Power Analysis Module: "
        reportText += self.PAMSerial + "\n"
        reportText += "Quarch Fixture: "
        reportText += self.FixtureSerial + "\n"
        reportText += "Quarch FW Versions: "
        reportText += "FW:" + self.Firmware + ", FPGA: " + self.Fpga + "\n"
        reportText += "\n"
        reportText += "Calibration Instruments#:\n"
        reportText += self.calInstrumentId + "\n"

        # perform uptime check and write to file
        if self.waitComplete != True:
            reportText += self.wait_for_up_time(desired_up_time=600, command="conf:runtime:fix:sec?")
            self.waitComplete = True

        return reportText

    def setConnections(self,loadConnection,hostPowerConnection,reset=False):
    #TODO Fix for using class variable.
        if reset:
            self.loadChannel = None
            self.hostPowerChannel = None

        # If current connections are correct
        if self.loadChannel == loadConnection and self.hostPowerChannel == hostPowerConnection:
            # do nothing
            pass

        # else connections need to change
        else:

            # we can't turn an individual port off (at the moment) so we turn both off first, then set anything that needs setting
            if loadConnection == None or hostPowerConnection == None:
                self.switchbox.sendCommand("connect off")

            if loadConnection != None:
                self.switchbox.sendCommand("connect " + self.loadPort + " " + self.loadConnectionPortDict[loadConnection])

            if hostPowerConnection != None:
                self.switchbox.sendCommand("connect " + self.hostPort + " " + self.hostConnectionPortDict[hostPowerConnection])

        self.loadChannel = loadConnection
        self.hostPowerChannel = hostPowerConnection



    def getSwitchbox(self):
        # CheckSwitchbox
        if self.switchbox is None:
            while (True):
                switchboxAddress = userSelectDevice(scanFilterStr=["QTL2536"], message="Select a calibration 6 Way Test Lead Switch.", nice=True)
                if switchboxAddress == "quit":
                    printText("User Quit Program")
                    sys.exit(0)
                try:
                    self.switchbox = quarchDevice(switchboxAddress)
                    break
                except:
                    printText("Unable to communicate with selected device!")
                    printText("")
                    switchboxAddress = None
                    raise
        return self.switchbox


    def clear_calibration(self):

        # set unit into calibration mode
        self.dut.sendCommand("write " + QTL2347.CALIBRATION_MODE_ADDR + " 0xaa55")
        self.dut.sendCommand("write " + QTL2347.CALIBRATION_MODE_ADDR + " 0x55aa")

        # clear all calibration registers
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V12_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
        
        # write 0xaa55 to register to calibration complete register to tell module it is calibrated
        self.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_COMPLETE_ADDR + " 0xaa55")
        
    def write_calibration(self):

        # write the calibration registers
        # erase the tag memory
        printText("Erasing TAG memory..")
        self.dut.sendCommand("write 0xa200 0x0020")
        # TODO: should check for completion here...
        # wait for 2 seconds for erase to complete
        # check busy
        while checkBit(self.dut.sendCommand("read 0xa200"),8):
            time.sleep(0.1)
        # write the tag memory
        printText("Programming TAG memory...")
        self.dut.sendCommand("write 0xa200 0x0040")        
        # check busy
        while checkBit(self.dut.sendCommand("read 0xa200"),8):
            time.sleep(0.1)

    def close_module(self):

        # reset the fixture FPGA
        self.dut.sendCommand("fixture:reset")

        #close the connection to the calibration instrument
        self.calInstrument.closeConnection()

    def close_all(self):

        #close all attached devices
        self.calInstrument.setLoadCurrent(0)
        self.calInstrument.closeConnection()
        self.powerModule.setConnections(None,None)

    class QTL2347Calibration (Calibration):

        def __init__(self):
            super().__init__()

        def init_cal(self,voltage):

            # TODO: No Power control at the moment
            # power up
            #self.powerModule.dut.sendAndVerifyCommand("power up")

            # set averaging to max
            self.powerModule.dut.sendAndVerifyCommand("rec:ave 32k")

            # set module into calibration mode (again?)
            self.powerModule.dut.sendCommand("write " + QTL2347.CALIBRATION_MODE_ADDR + " 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write " + QTL2347.CALIBRATION_MODE_ADDR + " 0x55aa")   # will not verify

            #Reset Keithley
            self.powerModule.calInstrument.reset()

        def meas_12v_volt(self):

            result = getFixtureData(self.powerModule.dut,"12V VOLT")
            return result

        def meas_12v_cur(self):

            result = getFixtureData(self.powerModule.dut,"12V CUR")
            return result

        def meas_3v3_volt(self):

            result = getFixtureData(self.powerModule.dut,"3V3 VOLT")
            return result

        def meas_3v3_cur(self):

            result = getFixtureData(self.powerModule.dut,"3V3 CUR")
            return result

        def meas_3v3_aux_volt(self):

            result = getFixtureData(self.powerModule.dut,"3V3_AUX VOLT")
            return result

        def meas_3v3_aux_cur(self):

            result = getFixtureData(self.powerModule.dut,"3V3_AUX CUR")
            return result

        # check connections to host power and load
        def checkLoadVoltage(self,voltage,tolerance):

            #self.powerModule.calInstrument.setReferenceCurrent(0)
            self.powerModule.calInstrument.setReferenceVoltage(voltage/1000,"1e-6")  # set Keithley to the required voltage but limit current to 1uA
            result = self.powerModule.calInstrument.measureLoadVoltage()*1000    # *1000 because we use mV but keithley uses volts
            # check result is in required range
            if (result >= voltage-tolerance) and (result <= voltage+tolerance):
                return True
            else:
                return False

        def finish_cal(self):

            #turn off load
            self.powerModule.calInstrument.disable()

            #turn off switch
            self.powerModule.setConnections(None,None)

            # turn dut to autoranging
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F0")

        def report(self,action,data):

            report = []

            # send to report file
            report.append("          Pass Level  +/-(" + str(self.absErrorLimit) + str(self.units) +" + " + str(self.relErrorLimit) + "%) \n")


            # check errors and generate report
            report.append('\n')

            if action == "calibrate":
               report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Raw Value ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + ' ' + '{0:>10}'.format('Pass'))
            elif action == "verify":
                report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + '   ' + '{0:>10}'.format('Pass'))

            report.append("==================================================================================================")

            # zero worst case error vars
            worstAbsError = 0
            worstRelError = 0
            worstRef = None
            overallResult = True

            # for each calibration reference
            for thisLine in data:
                reference = thisLine[1]
                ppmValue = thisLine[0]

                # for calibration, replace value with calibrated result
                if action =="calibrate":
                    calibratedValue = self.getResult(ppmValue)
                # otherwise just use ppmValue directly
                else:
                    calibratedValue = ppmValue

                # work out errors
                (actError,errorSign,absError,relError,result) = getError(reference,calibratedValue,self.absErrorLimit,self.relErrorLimit)

                # compare/replace with running worst case
                if absError >= worstAbsError:
                    if relError >= worstRelError:
                        worstAbsError = absError
                        worstRelError = relError
                        worstCase = errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%) @ " + '{:.3f}'.format(reference) + self.units

                # update overall pass/fail
                if result != True:
                    overallResult = False

                #generate report
                passfail = lambda x: "Pass" if x else "Fail"
                if action == "calibrate":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + '{:>10.1f}'.format(calibratedValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))
                elif action == "verify":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))

            report.append("==================================================================================================")
            report.append('\n')

            if action == "calibrate":
                report.append("Calculated Multiplier: " + str(self.multiplier.originalValue()) + ", Calculated Offset: " + str(self.offset.originalValue()))
                report.append("Stored Multiplier: " + str(self.multiplier.storedValue()) + ", Stored Offset: " + str(self.offset.storedValue()))
                report.append("Multiplier Register: " + self.multiplier.hexString(4) + ", Offset Register: " + self.offset.hexString(4))

            report.append("" + '{0:<35}'.format(self.title)+ '     '  +'{0:>10}'.format("Passed : ")+ '  '  + '{0:<5}'.format(str(overallResult))+ '     ' + '{0:>11}'.format( "worst case:")+ '  '  +'{0:>11}'.format(worstCase))
            report.append("\n\n\n")
            
            #Add to Test Summary? Do this here?
            passfail = lambda x: "Passed" if x else "Failed"

            return {"title":self.title,"result":overallResult,"worst case":worstCase,"report":('\n'.join(report))}

    class QTL2347_12V_VoltageCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "12V Voltage Calibration"
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

            super().init_cal("12v")

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("12V",None)
            
            # Check Host Power is not present
            while (super().checkLoadVoltage(500,500) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("12V",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_volt()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 12v voltage", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V12_VOLT_MULTIPLIER_ADDR)
            # get 12v voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V12_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v voltage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v voltage offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_12V_LeakageCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "12V Leakage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 50                 # 50uA = 1% of 5000 uA
            self.relErrorLimit = 0                  # 0%
            self.test_min = 1000                    # 1000mV
            self.test_max = 14400                   # 14.4V
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = False               # offset is not stored, don't care
            self.offset_int_width = 16               # offset is not stored, don't care
            self.offset_frac_width = 16              # offset is not stored, don't care

        def init(self):

            super().init_cal("12v")

            #set manual range, full averaging, low current mode
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F5")
            # clear the multiplier register by setting it to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")

            self.powerModule.setConnections("12V",None)
            
            # Check Host Power is not present
            while (super().checkLoadVoltage(500,500) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("12V",None,reset=True)


        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            # negate result because in this case the load is providing the power, not sinking it
            return -load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return load_get_volt(self.powerModule.calInstrument)

        def setCoefficients(self):

            # we don't apply the leakage calibration here because it provides uA leakage results and the current calibration uses raw ADC values
            # instead we will use it to correct the current calibration and apply it later
            pass

        def finish(self):
            #self.powerModule.calInstrument.setLoadCurrentRangeAuto()
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v leakage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V12_LEAKAGE_MULTIPLIER_ADDR)
            return coefficients

        def writeCoefficients(self,coefficents):

            # write 12v leakage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LEAKAGE_MULTIPLIER_ADDR + " " + coefficents["multiplier"])

    class QTL2347_12V_LowCurrentCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "12V Low Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2%
            self.test_min = 10          # 10uA
            self.test_max = 85000       # 85mA
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

            super().init_cal("12v")

            #set manual range, full averaging, 12v low current mode, 3v3 all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F4")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("12V","12V")
            
            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("12V","12V",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            voltage =  super().meas_12v_volt()
            leakage = voltage*self.powerModule.calibrations["12V"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["12V"]["Leakage"].offset.originalValue()
            return load_meas_cur(self.powerModule.calInstrument) + leakage

        def readVal(self):

            return super().meas_12v_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 12v Low Current", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V12_LOW_MULTIPLIER_ADDR)
            # get 12v low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V12_LOW_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v low current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v low current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LOW_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_12V_HighCurrentCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "12V High Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2000   # 2mA
            self.relErrorLimit = 1      # 1%
            self.test_min = 1000        # 1mA
            self.test_max = 4000000     # 4A
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

            super().init_cal("12v")

            #set manual range, full averaging, 12v high current mode, 3v3 all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F8")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("12V","12V")
            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("12V","12V",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            voltage =  super().meas_12v_volt()
            leakage = voltage*self.powerModule.calibrations["12V"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["12V"]["Leakage"].offset.originalValue()
            return load_meas_cur(self.powerModule.calInstrument) + leakage

        def readVal(self):

            return super().meas_12v_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 12v high current", result)

            # once we've completed low and high current we can set leakage on the fixture
            result = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_LEAKAGE_MULTIPLIER_ADDR + " " + self.powerModule.calibrations["12V"]["Leakage"].multiplier.hexString(4))

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V12_HIGH_MULTIPLIER_ADDR)
            # get 12v high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V12_HIGH_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v high current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v high current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V12_HIGH_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_3V3_VoltageCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Voltage Calibration"
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

            super().init_cal("3v3")

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("3V3",None)

            # Check Host Power is present
            while (super().checkLoadVoltage(500,500) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("3V3",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_3v3_volt()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 3.3v voltage", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 3v3 voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_VOLT_MULTIPLIER_ADDR)
            # get 3v3 voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 3v3 voltage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 3v3 voltage offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_3V3_LeakageCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Leakage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 50                 # 50uA = 1% of 5000 uA
            self.relErrorLimit = 0                  # 0%
            self.test_min = 1000                    # 1000mV
            self.test_max = 14400                   # 14.4V
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = False               # offset is not stored, don't care
            self.offset_int_width = 16               # offset is not stored, don't care
            self.offset_frac_width = 16              # offset is not stored, don't care

        def init(self):

            super().init_cal("3v3")

            #set manual range, full averaging, low current mode
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F5")
            # clear the multiplier register by setting it to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")

            self.powerModule.setConnections("3V3",None)

            # Check Host Power is present
            while (super().checkLoadVoltage(500,500) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("3V3",None,reset=True)


        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            # negate result because in this case the load is providing the power, not sinking it
            return -load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return load_get_volt(self.powerModule.calInstrument)

        def setCoefficients(self):

            # we don't apply the leakage calibration here because it provides uA leakage results and the current calibration uses raw ADC values
            # instead we will use it to correct the current calibration and apply it later
            pass

        def finish(self):
            #self.powerModule.calInstrument.setLoadCurrentRangeAuto()
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 3.3v leakage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_LEAKAGE_MULTIPLIER_ADDR)
            return coefficients

        def writeCoefficients(self,coefficents):

            # write 3.3v leakage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LEAKAGE_MULTIPLIER_ADDR + " " + coefficents["multiplier"])

    class QTL2347_3V3_LowCurrentCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Low Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2                  # 2uA
            self.relErrorLimit = 2                  # 2%
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

            super().init_cal("3v3")

            #set manual range, full averaging, 3.3v low current mode, 12v all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F1")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("3V3","3V3")

            # Check Host Power is present               
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("3V3","3V3",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            voltage =  super().meas_3v3_volt()
            leakage = voltage*self.powerModule.calibrations["3.3V"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["3.3V"]["Leakage"].offset.originalValue()
            return load_meas_cur(self.powerModule.calInstrument) + leakage

        def readVal(self):

            return super().meas_3v3_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 3.3v low current", result)
        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 3.3v low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_LOW_MULTIPLIER_ADDR)
            # get 3.3v low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_LOW_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 3.3v low current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 3.3v low current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LOW_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_3V3_HighCurrentCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V High Current Calibration"
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

            super().init_cal("3v3")

            #set manual range, full averaging, 3.3v high current mode, 12v all off (so we can detect we're connected to the wrong channel
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F2")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("3V3","3V3")

            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("3V3","3V3",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            voltage =  super().meas_3v3_volt()
            leakage = voltage*self.powerModule.calibrations["3.3V"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["3.3V"]["Leakage"].offset.originalValue()
            return load_meas_cur(self.powerModule.calInstrument) + leakage

        def readVal(self):

            return super().meas_3v3_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 3.3v high current", result)

            # once we've completed low and high current we can set leakage on the fixture
            result = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_LEAKAGE_MULTIPLIER_ADDR + " " + self.powerModule.calibrations["3.3V"]["Leakage"].multiplier.hexString(4))

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 3v3 high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_HIGH_MULTIPLIER_ADDR)
            # get 3v3 high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_HIGH_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 3v3 high current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 3v3 high current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_HIGH_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_3V3_AUX_VoltageCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Aux Voltage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2              # 2mV
            self.relErrorLimit = 1              # 1%
            self.test_min = 40                  # 40mV
            self.test_max = 14400               # 14.4V
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

            super().init_cal("3V3_AUX")

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("3V3_AUX",None)

            # Check Host Power is not present	    
            while (super().checkLoadVoltage(500,500) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("3V3_AUX",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_3v3_aux_volt()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 3.3v voltage", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 3v3 voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_AUX_VOLT_MULTIPLIER_ADDR)
            # get 3v3 voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_AUX_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 3v3 voltage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 3v3 voltage offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_3V3_AUX_LeakageCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Aux Leakage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 50                 # 50uA = 1% of 5000 uA
            self.relErrorLimit = 0                  # 0%
            self.test_min = 1000                    # 1000mV
            self.test_max = 14400                   # 14.4V
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = False               # offset is not stored, don't care
            self.offset_int_width = 16               # offset is not stored, don't care
            self.offset_frac_width = 16              # offset is not stored, don't care

        def init(self):

            super().init_cal("3V3_AUX")

            #set manual range, full averaging, low current mode
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.CALIBRATION_CONTROL_ADDR + " 0x00F5")
            # clear the multiplier register by setting it to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")

            self.powerModule.setConnections("3V3_AUX",None)

            # Check Host Power is not present	    
            while (super().checkLoadVoltage(500,500) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("3V3_AUX",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            # negate result because in this case the load is providing the power, not sinking it
            return -load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return load_get_volt(self.powerModule.calInstrument)

        def setCoefficients(self):

            # we don't apply the leakage calibration here because it provides uA leakage results and the current calibration uses raw ADC values
            # instead we will use it to correct the current calibration and apply it later
            pass

        def finish(self):
            #self.powerModule.calInstrument.setLoadCurrentRangeAuto()
            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 3.3v Aux leakage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_AUX_LEAKAGE_MULTIPLIER_ADDR)
            return coefficients

        def writeCoefficients(self,coefficents):

            # write 3.3v Aux leakage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_LEAKAGE_MULTIPLIER_ADDR + " " + coefficents["multiplier"])

    class QTL2347_3V3_AUX_CurrentCalibration (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Aux Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2          # 2uA
            self.relErrorLimit = 2          # 2%
            self.test_min = 100             # 100uA
            self.test_max = 400000          # 400mA
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 64
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("3V3_AUX")

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_OFFSET_ADDR + " 0x0000")

            self.powerModule.setConnections("3V3_AUX","3V3_AUX")

            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("3V3_AUX","3V3_AUX",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            # read device voltage and add leakage current to the reference
            voltage =  super().meas_3v3_aux_volt()
            leakage = voltage*self.powerModule.calibrations["3.3V Aux"]["Leakage"].multiplier.originalValue() + self.powerModule.calibrations["3.3V Aux"]["Leakage"].offset.originalValue()
            return load_meas_cur(self.powerModule.calInstrument) + leakage

        def readVal(self):

            return super().meas_3v3_aux_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 3.3v Aux low current", result)

            # once we've completed low and high current we can set leakage on the fixture
            result = self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_LEAKAGE_MULTIPLIER_ADDR + " " + self.powerModule.calibrations["3.3V Aux"]["Leakage"].multiplier.hexString(4))

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 3v3 low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_AUX_MULTIPLIER_ADDR)
            # get 3v3 low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL2347.V3_3_AUX_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 3v3 low current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 3v3 low current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL2347.V3_3_AUX_OFFSET_ADDR + " " + coefficients["offset"])

    class QTL2347_12V_VoltageVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "12V Voltage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2mV
            self.relErrorLimit = 1      # 1%
            self.test_min = 40          # 40mV
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("12V")

            self.powerModule.setConnections("12V",None)
            # Check Host Power is not present	    
            while (super().checkLoadVoltage(500,500) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("12V",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2347_12V_LowCurrentVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "12V Low Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2% tolerance
            self.test_min = 100         # 100uA
            self.test_max = 1000        # 1mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("12V")

            self.powerModule.setConnections("12V","12V")

            # Check Host Power is present
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,500) != True):
                input("Unexpected voltage detected at load, please check connections")
                self.powerModule.setConnections("12V","12V",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2347_12V_HighCurrentVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "12V High Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2000       # 2mA
            self.relErrorLimit = 1          # 1% tolerance
            self.test_min = 1000            # 1mA
            self.test_max = 4000000         # 4A
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("12v")

            self.powerModule.setConnections("12V","12V")
            # Check Host Power is present	    	    
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,500) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("12V","12V",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2347_3V3_VoltageVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Voltage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2mV
            self.relErrorLimit = 1      # 1%
            self.test_min = 40          # 40mV
            self.test_max = 6000        # 6V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("3V3")

            self.powerModule.setConnections("3V3",None)

            # Check Host Power is present
            while (super().checkLoadVoltage(500,500) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("3V3",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_3v3_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2347_3V3_LowCurrentVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Low Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2%
            self.test_min = 100         # 100uA
            self.test_max = 1000        # 1mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("3V3")

            self.powerModule.setConnections("3V3","3V3")

            # Check Host Power is present	    
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("3V3","3V3",None,reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_3v3_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2347_3V3_HighCurrentVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V High Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2000       # 2mA
            self.relErrorLimit = 1          # 1% tolerance
            self.test_min = 1000            # 1mA
            self.test_max = 4000000         # 4A
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("3V3")

            self.powerModule.setConnections("3V3","3V3")

            # Check Host Power is present	    
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("3V3","3V3",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_3v3_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2347_3V3_AUX_VoltageVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Aux Voltage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2mV
            self.relErrorLimit = 1      # 1%
            self.test_min = 40          # 40mV
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

            super().init_cal("3V3_AUX")

            self.powerModule.setConnections("3V3_AUX",None)

            # Check Host Power is not present	    
            while (super().checkLoadVoltage(500,500) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("3V3_AUX",None,reset=True)

        def setRef(self,value):

            return load_set_volt(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_3v3_aux_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2347_3V3_AUX_CurrentVerification (QTL2347Calibration):

        def __init__(self,powerModule):

            self.title = "3.3V Aux Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2%
            self.test_min = 100         # 100uA
            self.test_max = 400000      # 400mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("3V3_AUX")

            self.powerModule.setConnections("3V3_AUX","3V3_AUX")

            # Check Host Power is present	    
            while (super().checkLoadVoltage(QTL2347.LOAD_VOLTAGE,1000) != True):
            	input("Unexpected voltage detected at load, please check connections")
            	self.powerModule.setConnections("3V3_AUX","3V3_AUX",reset=True)

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_3v3_aux_cur()

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
        # populate 12V channel with calibrations
        self.calibrations["12V"] = {
            "Voltage":self.QTL2347_12V_VoltageCalibration(self),
            "Leakage":self.QTL2347_12V_LeakageCalibration(self),
            "Low Current":self.QTL2347_12V_LowCurrentCalibration(self),
            "High Current":self.QTL2347_12V_HighCurrentCalibration(self)
            }
        # populate 3V3 channel with calibrations
        self.calibrations["3.3V"] = {
            "Voltage":self.QTL2347_3V3_VoltageCalibration(self),
            "Leakage":self.QTL2347_3V3_LeakageCalibration(self),
            "Low Current":self.QTL2347_3V3_LowCurrentCalibration(self),
            "High Current":self.QTL2347_3V3_HighCurrentCalibration(self)
            }
        # populate 3V3_AUX channel with calibrations
        self.calibrations["3.3V Aux"] = {
            "Voltage":self.QTL2347_3V3_AUX_VoltageCalibration(self),
            "Leakage":self.QTL2347_3V3_AUX_LeakageCalibration(self),
            "Current":self.QTL2347_3V3_AUX_CurrentCalibration(self)
            }

        self.verifications = {}
        # populate 12V channel with verifications
        self.verifications["12V"] = {
            "Voltage":self.QTL2347_12V_VoltageVerification(self),
            "Low Current":self.QTL2347_12V_LowCurrentVerification(self),
            "High Current":self.QTL2347_12V_HighCurrentVerification(self)
            }
        # populate 3V3 channel with verifications
        self.verifications["3.3V"] = {
            "Voltage":self.QTL2347_3V3_VoltageVerification(self),
            "Low Current":self.QTL2347_3V3_LowCurrentVerification(self),
            "High Current":self.QTL2347_3V3_HighCurrentVerification(self)
            }
        # populate 3V3 channel with verifications
        self.verifications["3.3V Aux"] = {
            "Voltage":self.QTL2347_3V3_AUX_VoltageVerification(self),
            "Current":self.QTL2347_3V3_AUX_CurrentVerification(self)
            }

if __name__== "__main__":
    main()

