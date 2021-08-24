"""
Helper functions to parse API calls.
"""

def errorhandler(self, response, call):
    ret = False
    responsedata = response.json()
    if self.verbose == 'debug': print(responsedata)
    
    if 'data' not in responsedata: 
        if self.verbose: print(f'Error in {call} GraphQL call.')
    elif responsedata['data'] is None:
        if 'errors'in responsedata and 'message' in responsedata['errors'][0]:
            if self.verbose: print(responsedata['errors'][0]['message'])
        else:
            if self.verbose: print(f'Error in {call} GraphQL call.')
    elif call not in responsedata['data']:
        if self.verbose: print(f'Error in {call} GraphQL call.')
    elif responsedata['data'][call] is None:
        if 'errors'in responsedata and 'message' in responsedata['errors'][0]:
            if self.verbose: print(responsedata['errors'][0]['message'])
        else:
            if self.verbose: print(f'Error in {call} GraphQL call.')
    else:
        if responsedata['data'][call] == "success": ret = True
        elif responsedata['data'][call] == "failure": ret = False
        else: ret = responsedata['data'][call]
        
    return ret
