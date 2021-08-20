"""Day object, list of Prayer objects"""
from datetime import datetime
from prayer import Prayer

class Day:
    def __init__(self, fajr, dhor, asr, maghreb, icha, date):
        self.fajr = Prayer("fajr", fajr)
        self.dhor = Prayer("dhor", dhor)
        self.asr = Prayer("asr", asr)
        self.maghreb = Prayer("maghreb", maghreb)
        self.icha = Prayer("icha", icha)
        self.date = date
    
    def to_string(self):
        """Returns a string to show the daily prayers"""
        string = f"Date : {self.date} \n{self.fajr.name} : {self.fajr.time}",
        f" \n{self.fajr.name} : {self.dhor.time} \n{self.fajr.name} : {self.asr.time}\n",
        f"{self.fajr.name} : {self.maghreb.time} \n{self.fajr.name} : {self.icha.time}"
        return string

    def next_prayer(self):
        """Returns an object of the next prayer, based on current time of the system"""
        time = datetime.now().time()
        if time <= self.fajr.time:
            return self.fajr
        elif time <= self.dhor.time:
            return self.dhor
        elif time <= self.asr.time:
            return self.asr
        elif time <= self.maghreb.time:
            return self.maghreb
        elif time <= self.icha.time:
            return self.icha
        else:
            return None
