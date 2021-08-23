import os
import requests
import array
import json
import datetime 

from dotenv import load_dotenv
load_dotenv()


API_KEY = os.getenv('ARKESEL_API_KEY')


class APIKeyMissingError(Exception):
    pass

if API_KEY is None:
    raise APIKeyMissingError(
        "All methods require an API key. See "
        "https://sms.arkesel.com/user/sms-api/info "
        "for how to retrieve an API key from Arkesel "
    )


session = requests.Session()
session.params = {}
session.params['api_key'] = API_KEY

class ArkeselOtp():
    def __init__(self) -> None:
        pass

    def sendOtp(self, expiry, length , medium , message , number , sender_id , type):
        header = {"api-key":API_KEY,'Content-Type': 'application/json', 'Accept':'application/json'}
        SEND_OTP_URL = "https://sms.arkesel.com/api/otp/generate"

        payload ={
            "expiry": expiry,
            "length": length,
            "medium": medium,
            "message": message,
            "number": number,
            "sender_id": sender_id,
            "type": type
        }
    
        response = requests.post(SEND_OTP_URL, headers=header,json=payload)
        return response.json()
        #  print (response.text.encode('utf8'))
    # sendOtp( 5, 6, "sms","This is OTP from Source, %otp_code%","233248649732","Source","numeric")
    
    def verifyOtp(self , code , number):
        header = {"api-key":API_KEY,'Content-Type': 'application/json', 'Accept':'application/json'}
        VERIFY_OTP_URL = "https://sms.arkesel.com/api/otp/verify"

        payload ={
            "number": number,
            "code" : code
        }
    
        response = requests.post(VERIFY_OTP_URL, headers=header,json=payload)
        return response.json()
        # print (response.text.encode('utf8'))
    # verifyOtp(code , number)
