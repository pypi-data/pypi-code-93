#import telnetlib
import socket
import time
import logging,os
import sys
from quarchpy.calibration.deviceHelpers import locateMdnsInstr
from quarchpy.user_interface import *

'''
Prints out a list of calibration instruments nicely onto the terminal, numbering each unit
'''
def listCalInstruments(scanDictionary):
    if (not scanDictionary):
        print ("No instruments found to display")
    else:
        x = 1
        for k, v in scanDictionary.items():
            # these items should all be Keithley 2460 SMUs
            # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
            # we want to extract name, serial number and ip address
            ip = k
            # if we recognise the device, pull out Keithley serial number
            if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
                id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
            else:
                id = v  # else we don't recognise the device, return the whole identifier unmodified
            print (str(x) + " - " + id + "\t" + ip)
            x += 1

'''
Allows the user to select a test instrument
'''
def userSelectCalInstrument(scanDictionary=None, scanFilterStr="2460", title=None, message=None, tableHeaders= None, additionalOptions = None, nice=False):
    #Initiate values. Originals must be stored for the case of a rescan.
    originalOptions = additionalOptions
    if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
        nice = False
    if message is None: message = "Select the calibration instrument to use:"
    if title is None: title = "Select a calibration instrument"
    while(True): #breaks when valid user input given
        # Scan first, if no list is supplied
        if (scanDictionary is None):
            printText ("Scanning for instruments...")
            scanDictionary = foundDevices = locateMdnsInstr(scanFilterStr)

        deviceList = []

        if nice: #prep data for nice list selection,
            if additionalOptions is None: additionalOptions = ["Rescan", "Quit"]
            if (not scanDictionary):
                deviceList.append(["No instruments found to display"])
            else:
                for k, v in scanDictionary.items():
                    # these items should all be Keithley 2460 SMUs
                    # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
                    # we want to extract name, serial number and ip address
                    ip = k
                    # if we recognise the device, pull out Keithley serial number
                    if "Keithley 2460 " in v[:14]:  # currently we don't get here without this being true, but that may not be the case in future
                        name =v[:14]
                        serialNo = v[14:].split(".")[0]
                        deviceList.append([name,serialNo,ip])
                    else:
                        id = v  # else we don't recognise the device, return the whole identifier unmodified
                        deviceList.append([ip + "=" + id + " " + ip])
            adOp = []
            for option in additionalOptions:
                adOp.append([option]*3)
            userStr = listSelection(title=title, message=message, selectionList=deviceList, tableHeaders=["Name","Serial","IP Address"], nice=nice, indexReq=True, additionalOptions=adOp)[3] #Address will allways be 3 in this format


        else: #Prep data for test center
            if (not scanDictionary):
                deviceList.append("1=No instruments found to display")
            else:

                x = 1
                for k, v in scanDictionary.items():
                    # these items should all be Keithley 2460 SMUs
                    # form of the value is 'Keithley 2460 #04412428._http._tcp.local.'
                    # we want to extract name, serial number and ip address
                    ip = k
                    # if we recognise the device, pull out Keithley serial number
                    if "Keithley 2460 " in v[:14]:    # currently we don't get here without this being true, but that may not be the case in future
                        id = v[:14] + "\t" + v[14:].split(".")[0]   # ignore the name we've just matched, and take everything up to the first '.' this should be the serial number
                    else:
                        id = v  # else we don't recognise the device, return the whole identifier unmodified
                    deviceList.append(ip + "=" + id + "\t" + ip)
                    x += 1
            if additionalOptions is None:
                additionalOptions = "Rescan=Rescan,Quit=Quit"
            deviceList = ",".join(deviceList)
            userStr = listSelection(title=title,message=message,selectionList=deviceList, additionalOptions=additionalOptions)


            
        # Process the user response
        if (userStr == 'q' or userStr.lower() in "quit"):
            return "quit"
        elif (userStr == 'r' or userStr.lower() in "rescan"):
            scanDictionary = None
            additionalOptions = originalOptions
        else:
            # Return the address string of the selected instrument
            return userStr

'''
Class for control of Keithley source measure units for calibration purposes
'''
class keithley2460:

    '''
    Static method to locate available instruments. Returns disctionary, "IP_ADDRESS:DESCRIPTION-TEXT"
    '''
    @staticmethod
    def locateDevices():
        return None



    '''
    Init the class
    '''
    def __init__(self, connectionString):
        self.conString = connectionString
        self.connection = None
        self.idnString = "MODEL 2460"
        self.BUFFER_SIZE = 1024
        self.TIMEOUT = 120 #Changed to allow AIC calibration due to delay of meas:curr? when calibrating leakage.
        
    '''
    Open the connection to the instrument
    '''
    def openConnection (self, connectionString = None):
        # Connect TCP
        if (connectionString is not None):
            self.conString = connectionString
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.settimeout(self.TIMEOUT)
        logging.debug(os.path.basename(__file__) + ": opening connection: " + self.conString)
        self.connection.connect((self.conString,5025))
        # Clear errors, set to default state
        response = self.sendCommand ("*RST")
        # Send the IDN? command
        response = self.sendCommandQuery ("*IDN?")
        # Verify this looks like the expected instrument
        if (response.find (self.idnString) == -1):
            raise ValueError ("Connected device does not appear to be a keithley2460")
        
    '''
    Close the connection to the instrument
    '''
    def closeConnection (self):
        logging.debug(os.path.basename(__file__) + ": closing connection to Keithley ")
        self.connection.close()

    '''
    Attempts to force close any existing (LAN) socket connections
    '''
    def closeDeadConnections (self):
        deadSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        deadSocket.settimeout(self.TIMEOUT)
        deadSocket.connect((self.conString,5030))
        deadSocket.close()

        
    '''
    Send a command to the instrument and return the response from the query
    This should only be used for commands which expect a response
    '''
    def sendCommandQuery (self, commandString):
        retries = 1
        while retries < 5:
            try:
                # Send the command
                startTime= int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))
                # Read back the response data
                resultStr = self.connection.recv(self.BUFFER_SIZE).decode("utf-8")
                endTime = int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": received: " + resultStr)
                logging.debug(os.path.basename(__file__) + ": Time Taken : " + str(endTime-startTime) + " mS")
                resultStr = resultStr.strip ('\r\n\t')
                # If no response came back
                if (resultStr is None or resultStr == ""):
                    logging.error("resultStr = "+ resultStr)
                    if (self.getStatusEavFlag () == True):
                        errorStr = self.getNextError ()
                        self.clearErrors ()
                        raise ValueError ("Keithley query command did not run correctly: " + errorStr)
                    else:
                        raise ValueError ("The Keithley did not return a response")
                return resultStr
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": keithley command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on Keithley
                self.closeDeadConnections()
                # reopen connection to keithley
                self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.connection.settimeout(self.TIMEOUT)
                self.connection.connect((self.conString,5025))
                # increment retry counter
                retries = retries + 1
        raise TimeoutError (os.path.basename(__file__) + ": timed out while expecting a response")
        
    
    '''
    Sends a command to the instrument where a response is not expected.
    Status byte check is used to verify that the command does not flag an error
    If an error is found, it will be flushed and the first error text returned
    'OK' is returned on success
    '''    
    def sendCommand (self, commandString, expectedResponse = True):
        retries = 1
        while retries < 5:
            try:
                # Send the command
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))
                # Check for errors
                if (self.getStatusEavFlag () == True):
                    errorStr = self.getNextError ()
                    self.clearErrors ()
                    return errorStr
                else:
                    return "OK"
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": keithley command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on Keithley
                self.closeDeadConnections()
                # reopen connection to keithley
                self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.connection.settimeout(self.TIMEOUT)
                self.connection.connect((self.conString,5025))
                # increment retry counter
                retries = retries + 1
        raise TimeoutError (os.path.basename(__file__) + ": timed out while sending command to Keithley")
    
    '''
    Reset the instrument
    '''
    def reset (self):
        result = self.sendCommand("*RST")
        return result
        
    '''
    Enable/disable the outputs
    '''
    def setOutputEnable (self, enableState):
        if (enableState == True):
            result = self.sendCommand("OUTP ON")
        else:
            result = self.sendCommand("OUTP OFF")
            
        return result
        
    '''
    Return the output enable state as a boolean
    '''
    def getOutputEnable (self):
        result = self.sendCommandQuery ("OUTP?")
        if (int(result) == 1):
            return True
        else:
            return False
        
    '''
    Set the output voltage limit, in volts
    '''
    def setLoadVoltageLimit (self, voltValue):
        return self.sendCommand("SOUR:CURR:VLIM " + str(voltValue))
        
    '''
    Return the load voltage limit as a float
    '''
    def getLoadVoltageLimit (self):
        result = self.sendCommandQuery ("SOUR:CURR:VLIM?")
        return float(result)
        
    '''
    Switch the outputs to high impedance mode
    '''
    def setOutputMode (self, modeString):        
        modeString = modeString.upper()
        # validate modestring
        if modeString in ["HIMP","NORMAL","ZERO"]:
            # set the mode
            return self.sendCommand("OUTP:CURR:SMOD " + modeString)
        else:
            raise ValueError ("Invalid mode type specified: " + modeString)
            
        
        
    '''
    Returns the high impedance mode as a string
    '''
    def getOutputMode (self):
        return self.sendCommandQuery("OUTP:CURR:SMOD?");
        
    '''
    Changes the instrument into the specified measurement mode
    '''
    def setMeasurementMode (self, measModeString):
        measModeString = measModeString.upper()
        if (measModeString == "VOLT"):
            result = self.sendCommand("SENS:FUNC \"VOLT\"")
        elif (measModeString == "CURR"):
            result = self.sendCommand("SENS:FUNC \"CURR\"")
        else:
            raise ValueError ("Invalid mode type specified: " + measModeString)
            
        return result
            
    '''
    Return the current measurement mode as a string
    '''
    def getMeasurementMode (self):
        return self.sendCommandQuery("SENS:FUNC?").strip('\"')
        
    '''
    Changes the instrument into the specified source/output mode
    '''
    def setSourceMode (self, sourceModeString):
        sourceModeString = sourceModeString.upper()
        if sourceModeString in ["VOLT","CURR"]:
            result = self.sendCommand("SOUR:FUNC " + sourceModeString)
        else:
            raise ValueError ("Invalid mode type specified: " + sourceModeString)
        return result

    '''
    Return the source mode, as a string
    '''
    def getSourceMode (self):
        return self.sendCommandQuery("SOUR:FUNC?")
               
    '''
    Sets the number of measurements to be averaged together to return one voltage measurement
    '''
    def setAverageVoltageCount (self, measCount=1):
        self.sendCommand("VOLT:AVER:COUNT " + str(measCount))
        self.sendCommand("VOLT:AVER ON")
        
    '''
    Sets the number of measurements to be averaged together to return one current measurement
    '''
    def setAverageCurrentCount (self, measCount=1):
        self.sendCommand("CURR:AVER:COUNT " + str(measCount))
        self.sendCommand("CURR:AVER ON")
        
    '''
    Set the load/drain current to supply
    '''
    def setLoadCurrent (self, ampValue):        
        #load current should always be negative
        if (ampValue <= 0): 
            ampValue = -ampValue

        # set source current
        return self.sendCommand("SOUR:CURR -" + str(ampValue));


    '''
    Set the load/drain current range
    '''
    def setLoadCurrentRange(self, ampValue):
        # load current should always be negative
        if (ampValue <= 0):
            ampValue = -ampValue
        # set source current range
        val = self.sendCommand("SOUR:CURR:RANG " + str(ampValue));
        return val

    '''
    Set the load/drain current range to auto
    '''
    def setLoadCurrentRangeAuto(self):
        # set source current range to auto
        val = self.sendCommand("SOUR:CURR:RANG:AUTO ON");
        return val

    '''
    Sets the limit for the load current in Amps
    '''
    def setLoadCurrentLimit (self, ampValue):
        return self.sendCommand("SOUR:VOLT:ILIM " + str(ampValue));

    '''
    Gets the limit for the load current in Amps (float)
    '''
    def getLoadCurrentLimit (self):
        return self.sendCommandQuery("SOUR:VOLT:ILIM?");


    '''
    Gets the current load current, as set
    '''
    def getLoadCurrent (self):                  
        result = float((self.sendCommandQuery("SOUR:CURR?")))
        return -result
        
    '''
    Measures and returns a current value
    '''
    def measureLoadCurrent (self,count=4):
        self.setAverageCurrentCount(count)
        result = float((self.sendCommandQuery("MEAS:CURR?")))
        return -result
        
    '''
    Sets the load output voltage in Volts
    '''
    def setLoadVoltage (self, voltValue):
        return self.sendCommand("SOUR:VOLT " + str(voltValue))
        
    '''
    Gets the current load voltage value
    '''
    def getLoadVoltage (self):
        result = float((self.sendCommandQuery("SOUR:VOLT?")))
        return result
        
    '''
    Measures the current load voltage value
    '''
    def measureLoadVoltage (self,count=4):    
        self.setAverageVoltageCount(count)
        result = float(self.sendCommandQuery("MEAS:VOLT?"))
        return result
        
    '''
    Returns the status byte from the instrument (the result of the *STB? command)
    This is used to tell if the module is ready or has errored
    '''
    def getStatusByte (self, retries=4):
        tryCount = 0
        while tryCount <= retries:
            tryCount +=1
            # Read status byte
            resultStr = self.sendCommandQuery ("*STB?")
            # If we get junk, try again
            try:
                statInt = int(resultStr)
                return statInt
            except:
                logging.debug("Keithley is not responding with valid data retry " + str(tryCount))

        #If we have reached here we have excepet on every try and should raise a value error
        logging.error("Keithley is not responding with valid data : " + str(resultStr))
        raise ValueError ("Keithley is not responding with valid data")

    def printInstrumentStatus (self):
        stat = self.getStatusByte ()
        if (stat&1 != 0):
            print ("Measurement Summary Flag Set")
        if (stat&2 != 0):
            print ("Reserved Flag 1 Set")
        if (stat&4 != 0):
            print ("Error Available Flag Set")
        if (stat&8 != 0):
            print ("Questionable Event Flag Set")
        if (stat&16 != 0):
            print ("Message Available Flag Set")
        if (stat&32 != 0):
            print ("Enabled Standard Event Flag Set")
        if (stat&64 != 0):
            print ("Enabled Summary Bit Flag Set")
        if (stat&128 != 0):
            print ("Enabled Operation event Flag Set")
        if (stat == 0):
            print ("Status flags are clear")
        
    '''
    Returns the Measurement Summary Bit of the status information
    '''
    def getStatusMsbFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&1 != 0):
            return True
        else:
            return False;
            
    '''
    Returns the Question Summary Bit of the status information
    '''
    def getStatusQsbFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&8 != 0):
            return True
        else:
            return False;
            
    '''
    Returns the Error Available Bit of the status information
    '''
    def getStatusEavFlag (self):
        stat = self.getStatusByte ()
        # Meas bit is LSb
        if (stat&4 != 0):
            return True
        else:
            return False;
    
    '''
    Gets the next error from the instrument in a nice text form
    '''
    def getNextError (self):   
        errorStr = self.sendCommandQuery ("SYSTem:ERRor:NEXT?")
        return errorStr
    
    '''
    Clears all errors from the queue, so the status EAV flag is cleared
    '''
    def clearErrors (self):
        self.sendCommand (":SYSTem:CLEar")
        #loop = 0
        # Loop through and flush our all current errors
        #while (self.getStatusEavFlag () == True and loop < 10):
        #    print (self.getNextError ())
        #    loop += 1
    
    '''
    Sets the instrument to zero load current and returns the voltage
    Move to generic class?
    '''
    def measureNoLoadVoltage (self):
        self.setOutputEnable(False)
        self.setSourceMode("CURR")
        self.setLoadCurrent(0)
        self.setLoadVoltageLimit(15)
        self.setOutputEnable(True)
        return self.measureLoadVoltage()

    '''
    Sets the instrument load current
    Move to generic class?
    '''
    def setReferenceCurrent (self,value):
        if value >= 0:
            self.setOutputEnable(False)
            self.setSourceMode("CURR")
            self.setLoadVoltageLimit(15)
            self.setLoadCurrent(value)
            self.setOutputEnable(True)
        else:
            raise ValueError ("negative load current requested")

    '''
    Sets the instrument output voltage
    Move to generic class?
    '''
    def setReferenceVoltage (self,value,currentLimit="1e-1"):
        if value >= 0:
            self.setOutputEnable(False)
            self.setSourceMode("VOLT")
            self.setLoadCurrentLimit(currentLimit)
            self.setLoadVoltageLimit(15)
            self.setLoadVoltage(value)
            self.setOutputEnable(True)
        else:
            raise ValueError ("negative voltage requested") # this is possible but a bad idea unless we really want it

    '''
    Puts the into a safe state
    Move to generic class?
    '''
    def disable (self):
            self.setOutputEnable(False)
            self.setLoadCurrent(0)