'''
Author : surendra
Date   : 15 Apr 2019

logging is essential for automation.
** i will add more help soon***
'''


import logging
import os
import time

class Logging():
    def __init__(self, instance_name, log_file_location=''):
        self.logger = logging.getLogger(instance_name)
        self.instance_name = instance_name
        self.log_file_location = log_file_location
        if '.py' in log_file_location:
            self.log_file_location = TimeStampFile(log_file_location).getTimeStamp()
            
        self.fileLogger()
        self.screenLogger()
    
    def fileLogger(self, mode='w'):
        '''
        if you want to redirect your log messages to file.
        '''
        fh = logging.FileHandler(self.log_file_location, mode)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)8s - %(name)10s - %(message)s'))
        fh.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
    
    def screenLogger(self):
        '''
        if you want to redirect your log messages to standard console output.
        '''
        screen = logging.StreamHandler()
        screen.setLevel(logging.DEBUG)
        screen.setFormatter(logging.Formatter('%(asctime)s - %(levelname)8s - %(name)10s - %(message)s'))
        self.logger.addHandler(screen)
    
    def getLogger(self):
        '''
        returns object logger
        '''
        return self.logger
    
    def rootLogger(self):
        '''
        use this for the top most module in your flow.
        it will erase if any previous file handles.
        '''
        logger = logging.getLogger(self.instance_name)
        logger.handlers = []
        logging.basicConfig(format='%(asctime)s - %(levelname)8s - %(name)10s - %(message)s', level=logging.DEBUG, filename=self.log_file_location)
        self.screenLogger()
        return self.logger
        
    
class TimeStampFile():
    '''
    for timestamping any given file.
    it will take the file.. appends timestamp information. and returns new filename.
    '''
    def __init__(self, underscoreFile):
        '''
        please pass in parameter as __file__
        __file__ is a python default for current file name.
        '''
        self.underscoreFile = underscoreFile
    
    def getTimeStamp(self):
        '''
        reads the file. 
        add timestamp.
        replaces .py / .pyc notation to .log
        '''
        current_file    = self.underscoreFile
        real_path        = os.path.realpath(current_file)
        #basename         = os.path.basename(current_file)
        #preset_dir       = os.path.dirname(real_path)
        #print real_path, preset_dir, basename
        (fullpath, ext) = real_path.split('.')
        if 'py' in ext:
            ext = 'log'
        timestr = time.strftime("%Y%m%d_%H%M%S")
        return r'{}_{}.{}'.format(fullpath, timestr, ext)
        
        

if __name__ == '__main__':
    
    main_flow = 1
    sub_flow = 1
    
    # usage for your main program. copy paste in your main flow below line.
    if main_flow:
        from LoggingToolKit import Logging
        log_me = Logging(__name__, __file__)
        #(or) log_me = Logging(__name__, "robo.log")
        logger = log_me.rootLogger()
        
        print log_me.log_file_location
        
        logger.info('info message')
        logger.debug('debug message')
        logger.warning('warning message')
        logger.error('error message')
        logger.exception('exception capture')
    
    if sub_flow:
        from LoggingToolKit import Logging
        logger = Logging(__name__, __file__).getLogger()
        
    