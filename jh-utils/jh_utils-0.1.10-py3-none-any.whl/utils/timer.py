from datetime import datetime as dt

class Timer():    
    """    
    Timer class
    Declare a timer object that measure the time 
    of a running application
    """    
    def __init__(self, start_now = False):
        if start_now:
            self.start()

    def start(self):
        if hasattr(self,'start_time'):
            print('Started at: {}'.format(self.start_time))
        else:
            self.start_time = dt.now()
    
    def stop(self):
        if hasattr(self,'stop_time'):
            print('Stopped at: {}'.format(self.stop_time))
        else:
            self.stop_time = dt.now()
            self.duration = self.stop_time - self.start_time