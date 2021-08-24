import sys


class ServiceCommon:

    def __init__(self):
        pass

    @staticmethod
    def validate_response(resp):
        if not isinstance(resp, dict) and not isinstance(resp, list):
            sys.exit('Empty Response')
        elif 'message' in resp:
            sys.exit('Service Request Error')