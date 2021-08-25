# Module import
import numpy as np

#    def __init__(self, case_sensitive=False):
#
#        """Creates a detector parsing given data file"""
#        self.case_sensitive = case_sensitive

def __circle_area(ID):
    """ 
    Finds the area of a circle fiven by the specified turbine ID
    """
    a = round(np.pi * ID**2)
    return a

def request_data(ID):
    """
    Returns iSpin data for a specified turbine ID
    """

    if type(ID) == int:
        return __circle_area(ID)
    else:
        raise Exception("The provided turbine ID does not exists")


