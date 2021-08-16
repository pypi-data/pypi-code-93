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
from quarchpy.calibration.deviceHelpers import returnMeasurement
import quarchpy.calibration.calibrationConfig
import types
from time import sleep,time
from math import ceil
import re
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

class QTL1944 (PowerModule):

    CALIBRATION_MODE_ADDR       = '0xF000'
    V5_VOLT_OFFSET_ADDR         = '0xF002'
    V5_VOLT_MULTIPLIER_ADDR     = '0xF003'
    V5_LOW_OFFSET_ADDR          = '0xF004'
    V5_LOW_MULTIPLIER_ADDR      = '0xF005'
    V5_LEAKAGE_MULTIPLIER_ADDR  = '0xF006'
    V5_HIGH_OFFSET_ADDR         = '0xF007'
    V5_HIGH_MULTIPLIER_ADDR     = '0xF008'
    V12_VOLT_OFFSET_ADDR        = '0xF009'
    V12_VOLT_MULTIPLIER_ADDR    = '0xF00A'
    V12_LOW_OFFSET_ADDR         = '0xF00B'
    V12_LOW_MULTIPLIER_ADDR     = '0xF00C'
    V12_LEAKAGE_MULTIPLIER_ADDR = '0xF00D'
    V12_HIGH_OFFSET_ADDR        = '0xF00E'
    V12_HIGH_MULTIPLIER_ADDR    = '0xF00F'
    V5_OUTPUT_OFFSET_ADDR       = '0xF010'
    V12_OUTPUT_OFFSET_ADDR      = '0xF011'
    CALIBRATION_COMPLETE_ADDR    = '0xF012'  

    def __init__(self,dut):

        # Fixture Information
        self.enclosureSerial = None
        self.enclosurePosition = None
        self.PPMSerial = None
        self.calObjectSerial = None     # The serial number of the device that is being calibrated, i.e QTL1944 in HD PPM, Fixture in PAM
        self.idnStr = None
        self.Firmware = None
        self.Fpga = None
        self.calInstrument = None
        self.calInstrumentId = None
        self.switchbox = None
        self.waitComplete = False
        # set the name of this module
        self.name = "HD Programmable Power Module"
        self.dut = dut
        
        # Serial numbers (ensure QTL at start)
        self.enclosureSerial = self.dut.sendCommand("*ENCLOSURE?")
        if (self.enclosureSerial.find ("QTL") == -1):
            self.enclosureSerial = "QTL" + self.enclosureSerial
        # fetch the enclosure position
        self.enclosurePosition = self.dut.sendCommand("*POSITION?")
        self.PPMSerial = self.dut.sendCommand ("*SERIAL?")
        if (self.PPMSerial.find ("QTL") == -1):
            self.PPMSerial = "QTL" + self.PPMSerial
        # calObjectSerial Serial
        # Used for logging the module in TestCenter, In the case of a 1944 we use enclosure number
        self.calObjectSerial = self.enclosureSerial
        # Filename String
        self.filenameString = self.enclosureSerial + "-" + self.enclosurePosition
        # Code version (FPGA)
        self.idnStr = self.dut.sendCommand ("*IDN?")
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
            "Output Offset":self.HD12VOffsetCalibration(self ),
            "Voltage":self.HD12VVoltageCalibration(self),
            "Low Current":self.HD12VLowCurrentCalibration(self),
            "High Current":self.HD12VHighCurrentCalibration(self),
            "Leakage":self.HD12VLeakageCalibration(self)
            }
        # populate 5V channel with calibrations
        self.calibrations["5V"] = {
            "Output Offset":self.HD5VOffsetCalibration(self),
            "Voltage":self.HD5VVoltageCalibration(self),
            "Low Current":self.HD5VLowCurrentCalibration(self),
            "High Current":self.HD5VHighCurrentCalibration(self),
            "Leakage":self.HD5VLeakageCalibration(self)
            }

        self.verifications = {}
        # populate 12V channel with verifications
        self.verifications["12V"] = {
            "Output Offset":self.HD12VOffsetVerification(self),
            "Voltage":self.HD12VVoltageVerification(self),
            "Low Current":self.HD12VLowCurrentVerification(self),
            "High Current":self.HD12VHighCurrentVerification(self),
            "Leakage":self.HD12VLeakageVerification(self)
            }
        # populate 5V channel with verifications
        self.verifications["5V"] = {
            "Output Offset":self.HD5VOffsetVerification(self),
            "Voltage":self.HD5VVoltageVerification(self),
            "Low Current":self.HD5VLowCurrentVerification(self),
            "High Current":self.HD5VHighCurrentVerification(self),
            "Leakage":self.HD5VLeakageVerification(self)
            }

        self.listOfConnections = ["Please check that (red + black) force high on the switchbox is plugged into red + black force high on the keithley"]


    def specific_requirements(self):

        reportText=""

        # first wait for 6.5v regulator to be valid - this is necessary after a reset
        res = self.dut.getRuntime()
        # if the response was valid
        if res != None:
            if int(res) < 5:
                logging.debug("waiting " + str(5-int(res)) + "s for 6.5v regulator")
                time.sleep(5-int(res))
            else:
                pass
        # otherwise just wait 5s regardless
        else:
            logging.debug("waiting 5s for 6.5v regulator")
            time.sleep(5)

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

        # select a switchbox to use for calibration
        if "switchbox" in calibrationResources.keys():
            self.switchbox = calibrationResources["switchbox"]
        self.switchbox = self.getSwitchbox()
        calibrationResources["switchbox"] = self.switchbox

        # Write module specific report header to file
        reportText += "Quarch HD Programmable Power Module: "
        reportText += self.enclosureSerial + "\n"
        reportText += "Quarch Internal Serial: "
        reportText += self.PPMSerial + "\n"
        reportText += "Quarch FW Versions: "
        reportText += "FW:" + self.Firmware + ", FPGA: " + self.Fpga + "\n"
        reportText += "\n"
        reportText += "Calibration Instruments#:\n"
        reportText += self.calInstrumentId + "\n"

        # perform uptime check and write to file
        if self.waitComplete != True:
            reportText += self.wait_for_up_time(desired_up_time=600)
            self.waitComplete = True

        return reportText


    def getSwitchbox(self):
        # CheckSwitchbox
        if self.switchbox is None:
            while (True):
                switchboxAddress = userSelectDevice(scanFilterStr=["QTL2294"], message="Select a calibration switchbox.", nice=True, target_conn="rest")
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
        self.dut.sendCommand("write " + QTL1944.CALIBRATION_MODE_ADDR + " 0xaa55")
        self.dut.sendCommand("write " + QTL1944.CALIBRATION_MODE_ADDR + " 0x55aa")

        # clear all calibration registers
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_OUTPUT_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V12_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_OUTPUT_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_OFFSET_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_MULTIPLIER_ADDR + " 0x0000")
        self.dut.sendAndVerifyCommand("write " + QTL1944.V5_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")

        # write 0xaa55 to register 0xf012 to tell module it is calibrated
        self.dut.sendAndVerifyCommand("write " + QTL1944.CALIBRATION_COMPLETE_ADDR + " 0xaa55")
   


        
    def close_module(self):
        # reset the module
        printText("");
        printText("resetting the device...")
        printText("");
        #self = QTL1944(self.dut.resetDevice())
        self.dut.resetDevice(40)
        response = self.dut.sendCommand("*idn?")
        #close the connection to the calibration instrument
        self.calInstrument.closeConnection()

    def close_all(self):

        #close all attached devices
        self.calInstrument.setLoadCurrent(0)
        self.calInstrument.closeConnection()

    class HDCalibration (Calibration):

        def __init__(self):
            super().__init__()

        def init_cal(self,voltage):

            # get output mode
            mode = self.powerModule.dut.sendCommand("conf:out:mode?")

            # if output mode is not 5v, set it
            while mode != "5V":
                self.powerModule.dut.sendAndVerifyCommand("conf:out:mode 5v")
                #wait for module to change mode
                sleep(4)
                mode = self.powerModule.dut.sendCommand("conf:out:mode?")

            # power up
            self.powerModule.dut.sendAndVerifyCommand("power up")

            # disable pull down fets
            self.powerModule.dut.sendAndVerifyCommand("CONFig:OUTput:12v:PULLdown OFF")
            self.powerModule.dut.sendAndVerifyCommand("CONFig:OUTput:5v:PULLdown OFF")

            # set averaging to max
            self.powerModule.dut.sendAndVerifyCommand("rec:ave 32k")

            # set module into calibration mode (again?)
            self.powerModule.dut.sendCommand("write 0xf000 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write 0xf000 0x55aa")   # will not verify

            #Set switchbox to correct channel
            if voltage.upper() == "12V":
                self.powerModule.switchbox.sendAndVerifyCommand("connect 12v")
            elif voltage.upper() == "5V":
                self.powerModule.switchbox.sendAndVerifyCommand("connect 5v")
            else:
                raise ValueError("Invalid voltage specified")

            #check we are connected to the right channel
            if voltage.upper() == "12V":
                lower_limit = 11
                upper_limit = 13
                self.powerModule.dut.sendAndVerifyCommand("sig:12v:volt 12000")
            elif voltage.upper() == "5V":
                lower_limit = 4
                upper_limit = 6
                self.powerModule.dut.sendAndVerifyCommand("sig:5v:volt 5000")
            else:
                raise ValueError ("Invalid voltage specified")

            result = self.powerModule.calInstrument.measureNoLoadVoltage()


            while (result < lower_limit or result > upper_limit):
                if voltage.upper() == "12V":
                    lower_limit = 11
                    upper_limit = 13
                    self.powerModule.dut.sendAndVerifyCommand("sig:12v:volt 12000")
                elif voltage.upper() == "5V":
                    lower_limit = 4
                    upper_limit = 6
                    self.powerModule.dut.sendAndVerifyCommand("sig:5v:volt 5000")
                enclosure = self.powerModule.dut.sendCommand("*enclosure?")
                if enclosure.__contains__("1995"):
                    port = self.powerModule.dut.sendCommand("*POSITION?")
                    showDialog(title="Check load connection",message="\aPlease connect the calibration switch box to " + enclosure +" Port: " + port)
                else:
                    showDialog(title="Check load connection",message="\aPlease connect the calibration switch box to " + enclosure)

                self.powerModule.dut.sendAndVerifyCommand("run pow up")
                # Set switchbox to correct channel
                if voltage.upper() == "12V":
                    self.powerModule.switchbox.sendAndVerifyCommand("connect 12v")
                elif voltage.upper() == "5V":
                    self.powerModule.switchbox.sendAndVerifyCommand("connect 5v")
                else:
                    raise ValueError("Invalid voltage specified")
                printText("Verifying Connection...")
                result = self.powerModule.calInstrument.measureNoLoadVoltage()
                if (result < lower_limit or result > upper_limit):
                    printText("Connection is NOT correct, check cabling\n")
                else:
                    printText("Connection is correct\n")

            self.unitTemp = self.powerModule.dut.sendCommand('meas:temp unit?')
            self.v5Temp = self.powerModule.dut.sendCommand('meas:temp 5v?')
            self.v12Temp = self.powerModule.dut.sendCommand('meas:temp 12v?')

        def set_12v_volt(self,value):

            #set source voltage
            self.powerModule.dut.sendAndVerifyCommand("sig:12v:volt " + str(value))

            # this sleep is necessary to allow the output to update before taking more measurements
            # affects voltage calibration and leakage calibration
            sleep(0.2)

        def get_12v_volt(self):

            response = returnMeasurement(self.powerModule.dut,"sig:12v:volt?")
            return int(response[0])

        def meas_12v_volt(self):

            response = returnMeasurement(self.powerModule.dut,"meas:volt:12v?")

            # returnMeasurement() returns [value,units] we only need the value, which is actually ADC levels * 2^shift
            return int(response[0])

        def meas_12v_cur(self):

            response = returnMeasurement(self.powerModule.dut,"meas:cur 12v?")
            return float(response[0])*1000

        def set_5v_volt(self,value):

            #set source voltage
            self.powerModule.dut.sendAndVerifyCommand("sig:5v:volt " + str(value))

            # this sleep is necessary to allow the output to update before taking more measurements
            # affects voltage calibration and leakage calibration
            sleep(0.2)

        def get_5v_volt(self):

            #set source voltage
            response = returnMeasurement(self.powerModule.dut,"sig:5v:volt?")

            return int(response[0])

        def meas_5v_volt(self):

            response = returnMeasurement(self.powerModule.dut,"meas:volt:5v?")

            # returnMeasurement() returns [value,units] we only need the value, which is actually ADC levels * 2^shift
            return int(response[0])

        def meas_5v_cur(self):

            response = returnMeasurement(self.powerModule.dut,"meas:cur 5v?")
            return float(response[0])*1000

        def finish_cal(self):

            #turn off load
            self.powerModule.calInstrument.setReferenceCurrent(0)
            self.powerModule.calInstrument.disable()

            #turn off dut
            self.powerModule.dut.sendAndVerifyCommand("power down")
            # set power rails to nominal voltage
            self.powerModule.dut.sendAndVerifyCommand("sig:12v:volt 5000")
            self.powerModule.dut.sendAndVerifyCommand("sig:12v:volt 12000")
            # turn dut to autoranging
            self.powerModule.dut.sendAndVerifyCommand("write 0xf001 0x0100")

        def report(self,action,data):

            report = []
            reportTable=[]
            # send to report file
            report.append("\tPass Level  +/-(" + str(self.absErrorLimit) + str(self.units) +" + " + str(self.relErrorLimit) + "%) \n")
            report.append("Unit Temperature : "+ str(self.unitTemp) + "   5v Temperature : "+ str(self.v5Temp)+ "   12v Temperature : "+ str(self.v12Temp)) #5v 12v temp


            if action == "calibrate":
               tableHeaders = ['Reference', 'Raw Value', 'Result', 'Error', '+/-(Abs Error,% Error)', 'Pass']
            elif action == "verify":
                tableHeaders = ['Reference', 'Result', 'Error', '+/-(Abs Error,% Error)', 'Pass']

            # check errors and generate report
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
                    reportTable.append(
                        ["{:.3f}".format(reference), "{:.1f}".format(ppmValue), "{:.1f}".format(calibratedValue),
                         "{:.3f}".format(actError), (errorSign + "(" + str(absError) + str(self.units) + "," + str(
                            "{:.3f}".format(relError)) + "%)"), passfail(result)])

                    #report.append(displayTable(tableHeaders = tableHeaders, indexReq=False, printToConsole=False,align = "r", tableData=['{:>11.3f}'.format(reference),'{:>10.1f}'.format(ppmValue), '{:>10.1f}'.format(calibratedValue), "{:>10.3f}".format(actError), '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)"), '{0:>10}'.format(passfail(result))]))
                    #report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + '{:>10.1f}'.format(calibratedValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))
                elif action == "verify":
                    reportTable.append(["{:.3f}".format(reference), "{:.1f}".format(ppmValue), "{:.3f}".format(actError), (
                                errorSign + "(" + str(absError) + str(self.units) + "," + str(
                            "{:.3f}".format(relError)) + "%)"), passfail(result)])

                    #report.append(displayTable(tableHeaders = tableHeaders, indexReq=False, printToConsole=False,align = "r", tableData=['{:>11.3f}'.format(reference), '{:>10.1f}'.format(calibratedValue), "{:>10.3f}".format(actError), '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)"), '{0:>10}'.format(passfail(result))]))
                    #report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))


            # convert report from list of data to a table in string format.
            reportTable = displayTable(tableHeaders=tableHeaders, tableData=reportTable, printToConsole=False, indexReq=False, align="r")
            report.append(reportTable)


            if action == "calibrate":
                report.append("Calculated Multiplier: " + str(self.multiplier.originalValue()) + ", Calculated Offset: " + str(self.offset.originalValue()))
                report.append("Stored Multiplier: " + str(self.multiplier.storedValue()) + ", Stored Offset: " + str(self.offset.storedValue()))
                report.append("Multiplier Register: " + self.multiplier.hexString(4) + ", Offset Register: " + self.offset.hexString(4))

            report.append("" + '{0:<35}'.format(self.title)+ '     '  +'{0:>10}'.format("Passed : ")+ '  '  + '{0:<5}'.format(str(overallResult))+ '     ' + '{0:>11}'.format( "worst case:")+ '  '  +'{0:>11}'.format(worstCase))
            report.append("\n\n\n")
            
            #Add to Test Summary? Do this here?
            passfail = lambda x: "Passed" if x else "Failed"
            if passfail == "Failed":
                storeResult(self.title + ": "+ passfail(overallResult) + " worst case: " + worstCase)

            return {"title":self.title,"result":overallResult,"worst case":worstCase,"report":('\n'.join(report))}

        #"absErrorLimit":self.absErrorLimit, "relErrorLimit": self.relErrorLimit, "units": self.units, "unitTemp": self.unitTemp

    class HD12VOffsetCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V Output Offset Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 120     # the output can be within 1% of 12000mV = 120
            self.relErrorLimit = 0
            self.test_min = 10800
            self.test_max = 13200
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 3.538305666
            self.multiplier_signed = False
            self.multiplier_int_width = 16
            self.multiplier_frac_width = 16
            self.offset_signed = False
            self.offset_int_width = 13
            self.offset_frac_width = 0


        def init(self):

            # Initialise the module
            super().init_cal("12v")
            # clear the output offset register by setting it to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_OUTPUT_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)-11998   # this is the difference in mV between the current measured voltage and the nominal voltage

        def readVal(self):

            return (int(self.powerModule.dut.sendCommand("read 0x0006"),16)-0xD3F)*self.scaling  # this is the difference in mV between the current set point and the nominal voltage

        def setCoefficients(self):

            # set 12v output offset
            #self.powerModule.dut.sendCommand("write " + QTL1944.V12_OUTPUT_OFFSET_ADDR + " " + self.offset.hexString(4))
            result = self.powerModule.dut.sendAndVerifyCommand("write 0xf011 " + self.offset.hexString(4)) # negative offsets don't read back in 1.5 and below TODO do fpga check before calabration and ask user to update fpga is not high enough.
            logSimpleResult("Set 12v output offset", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v output offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_OUTPUT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            #check pass fail here and generate test point.
            # write 12v output offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_OUTPUT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VVoltageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V Voltage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 1
            self.relErrorLimit = 1
            self.test_min = 40
            self.test_max = 14400
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 2
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("12v")

            # set module into calibration mode (again?)
            self.powerModule.dut.sendCommand("write 0xf000 0xaa55")   # will not verify
            self.powerModule.dut.sendCommand("write 0xf000 0x55aa")   # will not verify
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_OFFSET_ADDR + " 0x0000")

            #set voltage to zero and wait 1 second to settle
            self.powerModule.dut.sendAndVerifyCommand("sig:12v:volt 0")
            sleep(1)

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_volt()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))
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
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_VOLT_MULTIPLIER_ADDR)
            # get 12v voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v voltage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v voltage offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VLowCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V Low Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2%
            self.test_min = 10      # 10uA
            self.test_max = 1000   # 1mA
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 16
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("12v")

            #set low current mode
            self.powerModule.dut.sendAndVerifyCommand("write 0xf001 0x0101")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_MULTIPLIER_ADDR + " 0x0000")
            #sendAndVerifyCommand(ppm,"write 0xf00b 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_OFFSET_ADDR + " 0x0000")
            #sendAndVerifyCommand(ppm,"write 0xf00c 0x0000")

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_OFFSET_ADDR + " " + self.offset.hexString(4))
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
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_LOW_MULTIPLIER_ADDR)
            # get 12v low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_LOW_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v low current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v low current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LOW_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VHighCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V High Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2000   # 2mA
            self.relErrorLimit = 1      # 1%
            self.test_min = 1000    # 1mA
            self.test_max = 4000000 # 4A
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

            #set high current mode
            self.powerModule.dut.sendAndVerifyCommand("write 0xf001 0x0102")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 12v high current", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_HIGH_MULTIPLIER_ADDR)
            # get 12v high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_HIGH_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 12v high current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 12v high current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_HIGH_OFFSET_ADDR + " " + coefficients["offset"])

    class HD12VLeakageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V Leakage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 50                 # 1% of 5000 uA
            self.relErrorLimit = 0                  #
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

            #set low current mode
            self.powerModule.dut.sendAndVerifyCommand("write 0xf001 0x0101")
            # clear the multiplier register by setting it to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
            #set load current to 5mA
            self.powerModule.calInstrument.setReferenceCurrent(0.005)
            #set voltage to test_min and wait for it to settle
            super().set_12v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            # return test current (5mA) - current measured by PPM
            # this is the correction we need to make to the measured current at the given voltage
            return 5000-(float(returnMeasurement(self.powerModule.dut,"meas:cur 12v?")[0])*1000)

        def readVal(self):

            # return the difference between nominal voltage and the current voltage
            # we use raw DAC values as it slightly more accurate (12v nominal voltage = 0xD3F = 11.9984 V
            # this is the value we will multiply to correct the current measurement
            return 0xD3F-int(self.powerModule.dut.sendCommand("read 0x0006"),16)

        def setCoefficients(self):

            result = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LEAKAGE_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            logSimpleResult("Set 12v leakage to device", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 12v leakage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V12_LEAKAGE_MULTIPLIER_ADDR)
            return coefficients

        def writeCoefficients(self,coefficents):

            # write 12v leakage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V12_LEAKAGE_MULTIPLIER_ADDR + " " + coefficents["multiplier"])

    class HD5VOffsetCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Output Offset Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 50     # the output can be within 1% of 5000mV = 50
            self.relErrorLimit = 0
            self.test_min = 4500
            self.test_max = 5500
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 3.538305666
            self.multiplier_signed = False
            self.multiplier_int_width = 16
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 13
            self.offset_frac_width = 0

        def init(self):

            super().init_cal("5v")

            # clear the output offset register by setting it to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_OUTPUT_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)-5000   # this is the difference in mV between the current measured voltage and the nominal voltage

        def readVal(self):

            return (int(self.powerModule.dut.sendCommand("read 0x0005"),16)-0x585)*self.scaling  # this is the difference in DAC levels between the current set point and the nominal voltage

        def setCoefficients(self):

            #self.powerModule.dut.sendCommand("write " + QTL1944.V5_OUTPUT_OFFSET_ADDR + " " + self.offset.hexString(4))
            result = self.powerModule.dut.sendAndVerifyCommand("write 0xf010 " + self.offset.hexString(4))    # negative offsets don't read back in 1.5 and below TODO FPGA check before config
            logSimpleResult("Set 5v output offset", result)
        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v output offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_OUTPUT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v output offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_OUTPUT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VVoltageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Voltage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 1
            self.relErrorLimit = 1
            self.test_min = 40
            self.test_max = 6000
            self.test_steps = 20
            self.units = "mV"
            self.scaling = 2
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("5v")

            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_OFFSET_ADDR + " 0x0000")

            #set voltage to zero and wait 1 second to settle
            self.powerModule.dut.sendAndVerifyCommand("sig:5v:volt 0")
            sleep(1)

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_5v_volt()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 5v voltage", result)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v voltage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_VOLT_MULTIPLIER_ADDR)
            # get 5v voltage offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_VOLT_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v voltage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 5v voltage offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_VOLT_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VLowCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Low Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2
            self.relErrorLimit = 2
            self.test_min = 10
            self.test_max = 1000
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 16
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal("5v")

            #set low current mode
            self.powerModule.dut.sendAndVerifyCommand("write 0xf001 0x0101")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_5v_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 5v low current", result)
        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v low current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_LOW_MULTIPLIER_ADDR)
            # get 5v low current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_LOW_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v low current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 5v low current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LOW_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VHighCurrentCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V High Current Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 2000
            self.relErrorLimit = 1
            self.test_min = 1000
            self.test_max = 4000000
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

            super().init_cal("5v")

            #set high current mode
            self.powerModule.dut.sendAndVerifyCommand("write 0xf001 0x0102")
            # clear the multiplier and offset registers by setting them to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_MULTIPLIER_ADDR + " 0x0000")
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_OFFSET_ADDR + " 0x0000")

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_5v_cur()

        def setCoefficients(self):

            result1 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            result2 = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_OFFSET_ADDR + " " + self.offset.hexString(4))
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set 5v high current", result)
        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v high current multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_HIGH_MULTIPLIER_ADDR)
            # get 5v high current offset
            coefficients["offset"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_HIGH_OFFSET_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v high current multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_MULTIPLIER_ADDR + " " + coefficients["multiplier"])
            # write 5v high current offset
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_HIGH_OFFSET_ADDR + " " + coefficients["offset"])

    class HD5VLeakageCalibration (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Leakage Calibration"
            self.powerModule = powerModule
            self.absErrorLimit = 50
            self.relErrorLimit = 0
            self.test_min = 1000
            self.test_max = 6000
            self.test_steps = 20
            self.units = "uA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 16
            self.offset_signed = True                # offset is not stored, don't care
            self.offset_int_width = 16               # offset is not stored, don't care
            self.offset_frac_width = 16              # offset is not stored, don't care


        def init(self):

            super().init_cal("5v")

            #set low current mode
            self.powerModule.dut.sendAndVerifyCommand("write 0xf001 0x0101")
            # clear the multiplier register by setting it to zero
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LEAKAGE_MULTIPLIER_ADDR + " 0x0000")
            #set load current to 5mA
            self.powerModule.calInstrument.setReferenceCurrent(0.005)

            #set voltage to test_min and wait for it to settle
            super().set_5v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            #return test current (5mA) - current measured by PPM
            return 5000-(float(returnMeasurement(self.powerModule.dut,"meas:cur 5v?")[0])*1000)

        def readVal(self):

            #return the difference between nominal voltage and the current voltage
            # we use raw DAC values as it slightly more accurate (12v nominal voltage = 0xD3F = 11.9984V not 12000mV
            # return nominal voltage - current set voltage
            return 0xD3F-int(self.powerModule.dut.sendCommand("read 0x0005"),16)

        def setCoefficients(self):

            result = self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LEAKAGE_MULTIPLIER_ADDR + " " + self.multiplier.hexString(4))
            logSimpleResult("Set 5v leakage", result)
        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

        def readCoefficients(self):

            coefficients = {}
            # get 5v leakage multiplier
            coefficients["multiplier"] = self.powerModule.dut.sendCommand("read " + QTL1944.V5_LEAKAGE_MULTIPLIER_ADDR)
            return coefficients

        def writeCoefficients(self,coefficients):

            # write 5v leakage multiplier
            self.powerModule.dut.sendAndVerifyCommand("write " + QTL1944.V5_LEAKAGE_MULTIPLIER_ADDR + " " + coefficients["multiplier"])

    class HD12VOffsetVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V Output Offset Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 0      # no absolute tolerance
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 10800       # 12v - 10%
            self.test_max = 13200       # 12v + 10%
            self.test_steps = 20
            self.units = "mV"


        def init(self):

            super().init_cal("12V")

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return super().get_12v_volt()

        def readVal(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD12VVoltageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V Voltage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 1      # 1mV
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 40          # 40mV
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "mV"


        def init(self):

            super().init_cal("12V")

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD12VLowCurrentVerification (HDCalibration):

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

    class HD12VHighCurrentVerification (HDCalibration):

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

    class HD12VLeakageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "12V Leakage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 0      # no absolute tolerance
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 1000       # 1V
            self.test_max = 14400       # 14.4V
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("12v")

            #set load current to 5mA
            self.powerModule.calInstrument.setReferenceCurrent(0.005)

            #set voltage to test_min and wait for it to settle
            super().set_12v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):

            super().set_12v_volt(value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_12v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VOffsetVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Output Offset Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 0      # no absolute tolerance
            self.relErrorLimit = 1      # 1% tolerance
            self.test_min = 4500        # 5v - 10%
            self.test_max = 5500        # 5v + 10%
            self.test_steps = 20
            self.units = "mV"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return super().get_5v_volt()

        def readVal(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VVoltageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Voltage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 1      # 1mV
            self.relErrorLimit = 1      # 1%
            self.test_min = 40          # 40mV
            self.test_max = 6000        # 6V
            self.test_steps = 20
            self.units = "mV"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return load_meas_volt(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_5v_volt()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VLowCurrentVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Low Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2      # 2uA
            self.relErrorLimit = 2      # 2%
            self.test_min = 100         # 100uA
            self.test_max = 1000        # 1mA
            self.test_steps = 20
            self.units = "uA"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_5v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VHighCurrentVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V High Current Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 2000       # 2mA
            self.relErrorLimit = 1          # 1% tolerance
            self.test_min = 1000            # 1mA
            self.test_max = 4000000         # 4A
            self.test_steps = 20
            self.units = "uA"

        def init(self):

           super().init_cal("5v")

        def setRef(self,value):

            load_set_cur(self.powerModule.calInstrument,value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_5v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class HD5VLeakageVerification (HDCalibration):

        def __init__(self,powerModule):

            self.title = "5V Leakage Verification"
            self.powerModule = powerModule
            self.absErrorLimit = 50      # 1% of 5000 uA
            self.relErrorLimit = 0          
            self.test_min = 1000         # 1V
            self.test_max = 6000         # 6V
            self.test_steps = 20
            self.units = "uA"

        def init(self):

            super().init_cal("5v")

            #set load current to 5mA
            self.powerModule.calInstrument.setReferenceCurrent(0.005)

            #set voltage to test_min and wait for it to settle
            super().set_5v_volt(self.test_min)
            sleep(1)

        def setRef(self,value):

            super().set_5v_volt(value)

        def readRef(self):

            return load_meas_cur(self.powerModule.calInstrument)

        def readVal(self):

            return super().meas_5v_cur()

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

if __name__== "__main__":
    main()

