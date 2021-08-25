# Functions
#def __init__(self, case_sensitive=False):
#
#    """Creates a detector parsing given data file"""
#    self.case_sensitive = case_sensitive
#username=None
#password=None


def __authorize():
    """
    User authentication
    """
    # Module import
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
    
    response = post_token()
    
    try:
        authResponse = response.json()
        accessToken = authResponse['access_token']
        authHeader_base = {'Authorization': 'Bearer '+accessToken}
    except:
        raise Exception('Invalid username and password')
    
    return authHeader_base



def __circle_area(ID):
    """ 
    Finds the area of a circle fiven by the specified turbine ID
    """
    import numpy as np
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


