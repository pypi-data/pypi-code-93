import requests
import json

class URLs:
    def __init__(self, response_format="json", ):
        self.format = response_format

        self.base_url = "http://13.251.45.210:80/"
        self.preprocess = 'preprocess'
        self.predictSentiment = 'predictSentiment'
        self.getAspect = 'extract_aspect_words'
        self.getOpinion = 'extract_opinion_units'
        self.getQualifer = "extract_qualifier"
        self.getAll = "do_all"
        self.getCt = "ct"

    def base_url(self):
        return self.base_url

    def preprocess_url(self):
        return self.base_url + self.preprocess

    def predictSentiment_url(self):
        return self.base_url + self.predictSentiment

    def getAspect_url(self):
        return self.base_url + self.getAspect

    def getOpinion_url(self):
        return self.base_url + self.getOpinion

    def getQualifier_url(self):
        return self.base_url + self.getQualifer

    def getAll_url(self):
        return self.base_url + self.getAll
    
    def getCt_url(self):
        return self.base_url + self.getCt

class Api():
    def __init__(self, response_format="json"):
        self.format = response_format
        self.url = URLs(response_format=response_format)
        self.header = {'Content-Type': 'application/json',
                       'Accept': 'application/json'}

    def __to_format(self, response):
        """A private method to return the API response in the desired format
            @param self - the object pointer
            @param response - response from the Ally Invest API
        """
        if response.status_code != 200:
            if response.status_code == 429:
                print("Too many requests.")
                exit()
            elif response.status_code == 414:
                print("URI too long, please chunk ticker symbols.")
                exit()
        if self.format == "json":
            return response.json()

    def __get_data(self, url, content):
        """A private method to return the requested data in the requested format
            for a given URL.
            @param self - the object pointer
            @param url - API URL to access
        """

        return self.__to_format(requests.post(url, data=json.dumps(content), headers=self.header))

    def get_preprocess(self, content):
        """Returns all of the user's accounts."""
        return self.__get_data(self.url.preprocess_url(), content)

    def get_SentimetnPredict(self, content):
        """Returns all of the user's accounts."""
        return self.__get_data(self.url.predictSentiment_url(), content)

    def get_AspectWords(self, content):
        """Returns all of the user's accounts."""
        return self.__get_data(self.url.getAspect_url(), content)

    def get_Opinion(self, content):
        """Returns all of the user's accounts."""
        return self.__get_data(self.url.getOpinion_url(), content)

    def get_Qualifer(self, content):
        """Returns all of the user's accounts."""
        return self.__get_data(self.url.getQualifier_url(), content)
    
    def get_All(self, content):
        """Returns all."""
        return self.__get_data(self.url.getAll_url(), content)

    def get_Ct(self, content):
        """Trigger CT"""
        return self.__get_data(self.url.getCt_url(), content)