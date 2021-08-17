from datetime import datetime as dt

class Timer():    
    """    
    Timer class
    Declare a timer object that measure the time 
    of a running application
    """    

    def __init__(self, start_now = False):
        self.start_time = None
        self.stop_time = None
        self.duration = None
        if start_now:
            self.start()
            
    def __repr__(self):
        return f'\n started: {str(self.start_time)} \n finished:{str(self.stop_time)} \n duration:{str(self.duration)}'

    def start(self):
        if self.start_time==None:
            self.start_time = dt.datetime.now()
        else:
            print('Started at: {}'.format(self.start_time))
    
    def stop(self):
        if self.stop_time==None:
            self.stop_time = dt.datetime.now()
            self.duration = self.stop_time - self.start_time
        else:
            print('Stopped at: {}'.format(self.stop_time))
            
class Timers():
    """    
    Multi Timer class
    Dictionary with multiple timers to divide steps in a aplication
    and can be called without declaring keys
    """    

    def __init__(self, start_now = False, n=1,timers_names=None):
        self.timers = dict()
        self.__starts = 0 
        self.__stops = 0

    def __repr__(self):
        return f'{self.timers}'
        
    def create_timer(self,timer_name):
        self.timers[timer_name] = Timer()
    
    def start(self,timer_name=None):
        if timer_name == None:
            timer_name = self.__starts
            self.__starts+=1
        
        self.create_timer(timer_name)
        self.timers[timer_name].start()
            
    def stop(self,timer_name=None):
        if timer_name == None:
            timer_name = self.__stops
            self.timers[timer_name].stop()
            self.__stops+=1
            return
        else:
            self.timers[timer_name].stop()