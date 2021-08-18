import requests
import json

class RestAPIController(object):

    def __init__(self, base_url, header_token_name=None, api_token=None, http_user=None, http_password=None):
        """ Initialize RestAPI
        
        Arguments:
            base_url {[type]} -- [description]
        
        Keyword Arguments:
            header_token_name {str} -- [header name to send api key if defined] (default: {None})
            api_token {str} -- [api key if required] (default: {None})
            http_user {str} -- [basic Auth user if required] (default: {None})
            http_password {str} -- [basic pass if required] (default: {None})
            if user/pass provided and apikey and header, api key will be used
        """
        self.base_url = base_url
        self.header_token_name = header_token_name
        self.api_token = api_token
        self.http_user = http_user
        self.http_password = http_password
        self.code_responses = [200,201,204]
        # self.session = requests.Session()


    def http_get(self, uri, params={}):
        """ HTTP REST GET, using params defined in params
        
        Arguments:
            uri {str} -- uri to add to base_url
        
        Keyword Arguments:
            params {dict} -- parameters to request (default: {{}} --- can be empty)
        
        Returns:
            [dict] -- request response content
        """
        full_path = '{}{}'.format(self.base_url,uri)
        if params:
            full_path = '{}?'.format(full_path)
            for index, key in enumerate(params.keys()):
                full_path = '{}{}={}'.format(full_path,key,params[key])
                if (index+1) != len(params.keys()):
                    full_path = '{}&'.format(full_path)
        response = requests.get(full_path, auth=(self.http_user,self.http_password))
        if response.status_code not in self.code_responses:
            if "message" in response.text:
                raise Exception(response.json()["message"])
            else:
                raise Exception(response.text)
        return response.json()

    
    def http_post(self, uri, data):
        """ HTTP REST POST, using data defined in data
        
        Arguments:
            uri {str} -- uri to add to base_url
            data {dict} -- data to be send in POST request
        
        Returns:
            [dict] -- request response content, raise an error if something wrong
        """
        full_path = '{}{}'.format(self.base_url,uri)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(full_path, data=json.dumps(data), headers=headers, auth=(self.http_user,self.http_password))
        if response.status_code not in self.code_responses:
            if "message" in response.text:
                print(response.json())
                raise Exception(response.json()["message"])
            else:
                raise Exception(response.text)
        return response.json()

    def http_put(self, uri, data):
        """ HTTP REST PUT, using data defined in data
        
        Arguments:
            uri {str} -- uri to add to base_url
            data {dict} -- data to be send in PUT request
        
        Returns:
            [dict] -- request response content
        """
        full_path = '{}{}'.format(self.base_url,uri)
        headers = {'Content-Type': 'application/json'}
        response = requests.put(full_path, data=json.dumps(data), headers=headers, auth=(self.http_user,self.http_password))
        if response.status_code not in self.code_responses:
            if "message" in response.text:
                raise Exception(response.json()["message"])
            else:
                raise Exception(response.text)
        return response.json() if response.text != "" else data

    def http_delete(self, uri):
        """ HTTP REST DELETE, using device_id in uri
        
        Arguments:
            uri {str} -- uri to add to base_url
        
        Returns:
            [str] -- request response content
        """
        full_path = '{}{}'.format(self.base_url,uri)
        response = requests.delete(full_path, auth=(self.http_user,self.http_password))
        if response.status_code not in self.code_responses:
            if "message" in response.text:
                raise Exception(response.json()["message"])
            else:
                raise Exception(response.text)
        return response.json() if response.text != "" else True