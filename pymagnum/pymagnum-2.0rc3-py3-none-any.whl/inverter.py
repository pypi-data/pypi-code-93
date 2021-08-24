
from magnum.magnum import Magnum
from magnum import __version__
from collections import OrderedDict
from copy import deepcopy

class InverterDevice:
    def __init__(self, trace=False):
        self.trace = trace
        self.data = OrderedDict()
        self.deviceData = OrderedDict()
        self.deviceData["device"] = Magnum.INVERTER
        self.deviceData["data"] = self.data
        self.data["revision"] = str(0.0)
        self.data["mode"] = 0
        self.data["mode_text"] = ""
        self.data["fault"] = 0
        self.data["fault_text"] = ""
        self.data["vdc"] = 0
        self.data["adc"] = 0
        self.data["VACout"] = 0
        self.data["VACin"] = 0
        self.data["invled"] = 0
        self.data["invled_text"] = ""
        self.data["chgled"] = 0
        self.data["chgled_text"] = ""
        self.data["bat"] = 0
        self.data["tfmr"] = 0
        self.data["fet"] = 0
        self.data["model"] = 0
        self.data["model_text"] = ""
        self.data["stackmode"] = 0
        self.data["stackmode_text"] = ""
        self.data["AACin"] = 0
        self.data["AACout"] = 0
        self.data["Hz"] = 0.0
        if self.trace:
            self.deviceData["trace"] = []

    def parse(self, packet):
        packetType = packet[0]
        unpacked = packet[2]
        if self.trace:
            self.deviceData["trace"].append([packetType,  packet[1].hex().upper()])
        if packetType in( Magnum.INV, Magnum.INV_C):
            self.data["mode"] = unpacked[0]
            self.data["fault"] = unpacked[1]
            self.data["vdc"] = unpacked[2] / 10
            self.data["adc"] = unpacked[3]
            self.data["VACout"] = unpacked[4]
            self.data["VACin"] = unpacked[5]
            self.data["invled"] = unpacked[6]
            if self.data["invled"] != 0:
                self.data["invled"] = 1
            self.data["chgled"] = unpacked[7]
            if self.data["chgled"] != 0:
                self.data["chgled"] = 1
            self.data["revision"] = str(round(unpacked[8] / 10, 2))
            self.data["bat"] = unpacked[9]
            self.data["tfmr"] = unpacked[10]
            self.data["fet"] = unpacked[11]
            self.data["model"] = unpacked[12]
            if packetType == Magnum.INV:
                self.data["stackmode"] = unpacked[13]
                self.data["AACin"] = unpacked[14]
                self.data["AACout"] = unpacked[15]
                self.data["Hz"] = round(unpacked[16] / 10, 2)
            else:
                self.data["stackmode"] = 0
                for key in ["AACin","AACout","Hz"]:
                    self.data.pop(key, '')
            self.set_stackmode_text()
        #
        #    (Model <= 50) means 12V inverter
        #    (Model <= 107) means 24V inverter
        # 	 (Model < 150) means 48V inverter
        #
            if self.data["model"] <= 50:
                # voltage = 12
                Magnum.multiplier = 1
            elif self.data["model"] <= 107:
                # voltage = 24
                Magnum.multiplier = 2
            elif self.data["model"] <= 150:
                # voltage = 48
                Magnum.multiplier = 4
            self.set_fault_text()
            self.set_chgled_text()
            self.set_invled_text()
            self.set_mode_text()
            self.set_model_text()
         

    def set_fault_text(self):
        faults = {
            0x00: "None",
            0x01: "STUCK RELAY",
            0x02: "DC OVERLOAD",
            0x03: "AC OVERLOAD",
            0x04: "DEAD BAT",
            0x05: "BACKFEED",
            0x08: "LOW BAT",
            0x09: "HIGH BAT",
            0x0A: "HIGH AC VOLTS",
            0x10: "BAD_BRIDGE",
            0x12: "NTC_FAULT",
            0x13: "FET_OVERLOAD",
            0x14: "INTERNAL_FAULT4",
            0x16: "STACKER MODE FAULT",
            0x18: "STACKER CLK PH FAULT",
            0x17: "STACKER NO CLK FAULT",
            0x19: "STACKER PH LOSS FAULT",
            0x20: "OVER TEMP",
            0x21: "RELAY FAULT",
            0x80: "CHARGER_FAULT",
            0x81: "High Battery Temp",
            0x90: "OPEN SELCO TCO",
            0x91: "CB3 OPEN FAULT"
        }
        if self.data["fault"] in faults:
            self.data["fault_text"] = faults[self.data["fault"]]

    def set_chgled_text(self):
            self.data["chgled_text"] = "Off" if self.data["chgled"] == 0 else "On"

    def set_invled_text(self):
        self.data["invled_text"] = "Off" if self.data["invled"] == 0 else "On"

    def set_mode_text(self):
        modes = {
            0x00:   "Standby",
            0x01:   "EQ",
            0x02:   "FLOAT",
            0x04:   "ABSORB",
            0x08:   "BULK",
            0x09:   "BATSAVER",
            0x10:   "CHARGE",
            0x20:   "Off",
            0x40:   "INVERT",
            0x50:   "Inverter_Standby",
            0x80:   "SEARCH"
        }
        if self.data["mode"] in modes:
            self.data["mode_text"] = modes[self.data["mode"]]
        else:
            self.data["mode_text"] = "??"

    def set_model_text(self):

        if self.data["model"] in Magnum.inverter_models:
            self.data["model_text"] = Magnum.inverter_models[self.data["model"]]
        else:
            self.data["model_text"] = "Unknown"

    def set_stackmode_text(self):
        modes = {
            0x00:  "Stand Alone",
            0x01:  "Parallel stack - master",
            0x02:  "Parallel stack - slave",
            0x04:  "Series stack - master",
            0x08:  "Series stack - slave"
        }
        if self.data["stackmode"] in modes:
            self.data["stackmode_text"] = modes[self.data["stackmode"]]
        else:
            self.data["stackmode_text"] = "Unknown"

    def getDevice(self):
        device = deepcopy(self.deviceData)
        if self.trace:
            self.deviceData["trace"] = []
        return device

