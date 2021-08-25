from requests import Request, Session
from requests import sessions
from requests.packages.urllib3 import add_stderr_logger
from requests.packages.urllib3.util.retry import Retry
import json

from requests.sessions import HTTPAdapter

class URLs:
    def __init__(self, response_format="json", ):
        self.format = response_format

        self.base_url = "http://13.212.164.75:80/%s?limmit={}"
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
        url = self.base_url % self.preprocess
        return url

    def predictSentiment_url(self):
        url = self.base_url % self.predictSentiment
        return url

    def getAspect_url(self):
        url =  self.base_url % self.getAspect
        return url

    def getOpinion_url(self):
        url =  self.base_url % self.getOpinion
        return url

    def getQualifier_url(self):
        url =  self.base_url % self.getQualifer
        return url

    def getAll_url(self):
        url = self.base_url % self.getAll
        return url
    
    def getCt_url(self):
        url = self.base_url % self.getCt
        return url

class Api():
    def __init__(self, response_format="json"):
        self.format = response_format
        self.url = URLs(response_format=response_format)
        self.header = {'Content-Type': 'application/json',
                       'Accept': 'application/json',
                       'Accept-Encoding': 'message/rfc822'}
        self.sessions = []
        self.retry = Retry(connect=3, backoff_factor=0.5)
        self.adapter = HTTPAdapter(max_retries=self.retry)
        # self.session = Session()
        # retry = Retry(connect=3, backoff_factor=0.5)
        # adapter = HTTPAdapter(max_retries=retry)
        # self.session.mount('http://', adapter)

    def get_sessions(self):
        return len(self.sessions)

    def close_session(self, id):
        self.sessions[id].close()
    
    def close_all_session(self):
        for session in self.sessions:
            session.close()

    def open_new_session(self):
        session = Session()
        session.mount('http://', self.adapter)
        self.sessions.append()


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

    def __get_data(self, session_id, url, content):
        """A private method to return the requested data in the requested format
            for a given URL.
            @param self - the object pointer
            @param url - API URL to access
        """
        req = Request('POST',url, data=json.dumps(content), headers=self.header)
        prep = req.prepare()
        resq = self.sessions[session_id].send(prep,
        stream=None,
        verify=None
        )
        return resq 

    def get_preprocess(self, session_id, content):
        """Returns all of the user's accounts."""
        return self.__get_data(session_id, self.url.preprocess_url(), content)

    def get_SentimetnPredict(self, session_id, content):
        """Returns all of the user's accounts."""
        return self.__get_data(session_id, self.url.predictSentiment_url(), content)

    def get_AspectWords(self, session_id, content):
        """Returns all of the user's accounts."""
        return self.__get_data(session_id, self.url.getAspect_url(), content)

    def get_Opinion(self, session_id, content):
        """Returns all of the user's accounts."""
        return self.__get_data(session_id, self.url.getOpinion_url(), content)

    def get_Qualifer(self, session_id, content):
        """Returns all of the user's accounts."""
        return self.__get_data(session_id, self.url.getQualifier_url(), content)
    
    def get_All(self, session_id, content):
        """Returns all."""
        return self.__get_data(session_id, self.url.getAll_url(), content)

    def get_Ct(self, session_id, content):
        """Trigger CT"""
        return self.__get_data(session_id, self.url.getCt_url(), content)