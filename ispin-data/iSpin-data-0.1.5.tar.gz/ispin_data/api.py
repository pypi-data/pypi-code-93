# Global variables
username = None
password = None


# Functions
#def __init__(self, case_sensitive=False):
#
#    """Creates a detector parsing given data file"""
#    self.case_sensitive = case_sensitive



def __authorize():
    """
    User authentication
    """

    import requests
    from retry import retry
    global username
    global password
    requests.packages.urllib3.disable_warnings()
  
    # Get access token...
    parameters = {'grant_type': 'password', 'username': username, 'password':password}
    
    @retry(tries=2, delay=30) # Retry twice.
    def post_token():      
        __baseUrl = "https://dc.romowind.net/api"
        response = requests.post(__baseUrl + "/token", data=parameters, verify=False)
        if (response.status_code == 200):
            print("*** Authenticated ***")
        return response

    if (username==None) & (password==None):
        raise Exception("Please provide your username and password as follows:\n import ispin_data.api as ispin\n ispin.username = 'your_username'\n ispin.password = 'your_password'")
        
    response = post_token()
    
    try:
        authResponse = response.json()
        accessToken = authResponse['access_token']
        authHeader_base = {'Authorization': 'Bearer '+accessToken}
    except:
        raise Exception('Invalid username and password')
    
    return authHeader_base



def request_overview():
    """
    Loads an overview of the iSpin installations
    """  
    
    import requests
    import pandas as pd

    # Obtaining authentication token
    authHeader = __authorize()
    
    # Requesting the turbines data
    __baseUrl = "https://dc.romowind.net/api"
    URL = __baseUrl + '/turbines'
    response = requests.get(URL, headers=authHeader, verify=False)
    Dataresponse = response.json()
    
    # Formatting the output data frame
    df = pd.DataFrame(Dataresponse)
    df = df.set_index('id')
    
    return df






















def __circle_area_calc(ID):
    """ 
    Finds the area of a circle fiven by the specified turbine ID
    """
    import numpy as np
    a = round(np.pi * ID**2)
    return a

def circle_area(ID):
    """
    Returns iSpin data for a specified turbine ID
    """

    if type(ID) == int:
        return __circle_area_calc(ID)
    else:
        raise Exception("The provided turbine ID does not exists")


