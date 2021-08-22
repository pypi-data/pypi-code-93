import requests

class Client:

    access_token = None 
    refresh_token = None 

    def __init__(self, email, password, licence_type):
        self.email = email
        self.password = password
        self.licence_type = licence_type

    def login(self):

        try:
            
            body = { "Email" : self.email, "Password" : self.password}

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8"}

            url = "https://www.37austen.com/api/login"

            response = requests.post(url, headers = headers, json = body)

            resp = response.json()
            
            self.access_token = resp['access_token']
            self.refresh_token = resp['refresh_token']

        except:

            print({"Error":{"Type":"Login failure."}})   

    def token_refresh(self):

        try:

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8", "Authorization" : "Bearer " + self.refresh_token}

            url = "https://www.37austen.com/api/refresh"

            response = requests.post(url, headers = headers)

            resp = response.json()

            self.access_token = resp['access_token']

            print("Token has been successfully refreshed.")  

        except:

            print({"Error":{"Type":"Token refresh failure."}})   

    def future_movement(self, data):

        if not isinstance(data,dict):

            return({"Error":{"Type":"The submitted price data must be submitted as a dict."}})

        try:
            body = data

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8", "Authorization" : "Bearer "+ self.access_token}

            url = "https://www.37austen.com/api/" + f"{self.licence_type}" + "/futuremovement"

            response = requests.post(url, headers = headers, json = body)

            return(response.json())

        except:

            print({"Error":{"Type":"Function failure."}}) 

    def future_movement_group(self, data):
    
        if not isinstance(data,dict):

            return({"Error":{"Type":"The submitted price data must be submitted as a dict."}})

        try:
            
            body = data

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8", "Authorization" : "Bearer " + f"{self.access_token}"}

            url = "https://www.37austen.com/api/" + f"{self.licence_type}" + "/futuremovement/group"

            response = requests.post(url, headers = headers, json = body)

            return(response.json())

        except:

            print({"Error":{"Type":"Function failure."}}) 

    def future_movement_fx(self, data):
        
        if not isinstance(data,dict):

            return({"Error":{"Type":"The submitted price data must be submitted as a dict."}})

        try:

            body = data

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8", "Authorization" : "Bearer " + f"{self.access_token}"}

            url = "https://www.37austen.com/api/" + f"{self.licence_type}" + "/futuremovement/fx"

            response = requests.post(url, headers = headers, json = body)

            return(response.json())

        except:

            print({"Error":{"Type":"Function failure."}}) 

    def future_movement_token(self, data):
        
        if not isinstance(data,dict):

            return({"Error":{"Type":"The submitted price data must be submitted as a dict."}})

        try:
            
            body = data

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8", "Authorization" : "Bearer " + f"{self.access_token}"}

            url = "https://www.37austen.com/api/" + f"{self.licence_type}" + "/futuremovement/token"

            response = requests.post(url, headers = headers, json = body)

            return(response.json())

        except:

            print({"Error":{"Type":"Function failure."}}) 

    def correlation(self, data):
        
        if not isinstance(data,dict):

            return({"Error":{"Type":"The submitted price data must be submitted as a dict."}})

        try:
            
            body = data

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8", "Authorization" : "Bearer " + f"{self.access_token}"}

            url = "https://www.37austen.com/api/" + f"{self.licence_type}" + "/correlation"

            response = requests.post(url, headers = headers, json = body)

            return(response.json())
    
        except:

            print({"Error":{"Type":"Function failure."}}) 


    def reset_password(self, data):
        
        if not isinstance(data,dict):

            return({"Error":{"Type":"The submitted price data must be submitted as a dict."}})

        try:
            
            body = data

            headers = {"Content-Type" : "application/json", "Accept" : "application/json; charset=UTF-8", "Authorization" : "Bearer " + f"{self.access_token}"}

            url = "https://www.37austen.com/api/resetpassword"

            response = requests.post(url, headers = headers, json = body)

            return(response.json())
    
        except:

            print({"Error":{"Type":"Function failure."}}) 