import os
import requests
import array

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

class ArkeselSMS(object):
    def __init__(self) :
        pass
    

    def sendSms(self,sender:str, message: str, recipients: array.array ):
        header= {"api-key":API_KEY,'Content-Type':'application/json','Accept':'application/json'}
        SEND_SMS_URL="https://sms.arkesel.com/api/v2/sms/send"
        payload ={
            "sender":sender,
            "message":message,
            "recipients": recipients 
        }
        response = requests.post(SEND_SMS_URL, headers=header,json=payload)
        return response.json()
        # print (response.text.encode('utf8'))
        # print(response.status_code)
    # sendSms('Trial','just trying this',['233248649732'])


    def scheduledSms(self , sender:str,message:str,recipients:array.array,scheduled_date:str):
        header = {"api-key":API_KEY , 'Content-Type': 'application/json', 'Accept':'application/json'}
        SEND_SMS_URL = "https://sms.arkesel.com/api/v2/sms/send"

        payload ={
            "sender":sender,
            "message":message,
            "recipients": recipients,
            "scheduled_date" : scheduled_date
        }
        response = requests.post(SEND_SMS_URL, headers=header,json=payload)
        return response.json()
        # print (response.text)
    # scheduledSms('Trial','just trying this',['0248649732'],"2021-08-02 12:07 PM")

 
    def webhookSms(self , sender:str, message:str, recipients:array.array, callback_url:str):
        header = {"api-key":API_KEY , 'Content-Type': 'application/json', 'Accept':'application/json'}
        SEND_SMS_URL = "https://sms.arkesel.com/api/v2/sms/send"

        payload ={
            "sender":sender,
            "message":message,
            "recipients": recipients,
            "callback_url" : callback_url
        }
        response = requests.post(SEND_SMS_URL, headers=header,json=payload)
        # print (response.status_code)
        return response.json()
    
    
    def sandBox(self , sender:str, message:str, recipients:array.array, sandbox:bool):
        header = {"api-key":API_KEY , 'Content-Type': 'application/json', 'Accept':'application/json'}
        SEND_SMS_URL = "https://sms.arkesel.com/api/v2/sms/send"

        payload ={
            "sender":sender,
            "message":message,
            "recipients": recipients,
            "sandbox" : sandbox
        }
        response = requests.post(SEND_SMS_URL, headers=header,json=payload)
        # print (response.status_code)
        return response.json()


    def voice_sms(self , voice_file:str, recipients:array.array):
       URL = "https://sms.arkesel.com/api/v2/sms/voice/send"
       header = {"api-key":API_KEY , 'Content-Type': 'application/json', 'Accept':'application/json'}
       payload={
           "voice_file":voice_file,
           "recipients":recipients
       }
       response = requests.post(URL, headers=header,json=payload)
       return response.json()
    #    print(response.text)

   
    def send_group_sms(self, sender:str , group_name:str , message:str):
        URL = "https://sms.arkesel.com/api/v2/sms/send/contact-group"
        header = {"api-key":API_KEY , 'Content-Type': 'application/json', 'Accept':'application/json'}
        payload ={
            "sender":sender,
            "group_name":group_name,
            "message":message,
        }

        response = requests.post(URL, headers=header,json=payload)
        return response.json()
        # print (response.text)
    # send_group_sms("test","TEST GROUP","Here's a message")


class SmsInfo(object):
    def __init__(self) :
        pass
           
       
    def smsBalance(self):
        header = {"api-key":API_KEY ,  'Content-Type': 'application/json', 'Accept':'application/json'}
        BALANCE_URL =   "https://sms.arkesel.com/api/v2/clients/balance-details"
        response = session.get(BALANCE_URL,headers=header)
        # print (response.text.encode('utf8'))
        return response.json()




    def smsDetails(self, DETAILS_URL):
        # DETAILS_URL = "https://sms.arkesel.com/api/v2/sms"/MESSAGE_ID
        header = {"api-key":API_KEY , 'Content-Type': 'application/json', 'Accept':'application/json'}
        response =  requests.get(DETAILS_URL , headers=header)
        return response.json()
        # print (response.text.encode('utf8'))
    # smsDetails("https://sms.arkesel.com/api/v2/sms/15332050")
