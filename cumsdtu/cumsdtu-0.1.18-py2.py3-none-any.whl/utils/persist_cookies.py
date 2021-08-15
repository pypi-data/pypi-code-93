import logging
import jsonpickle

from requests import Session
from requests.cookies import RequestsCookieJar
from cumsdtu.exceptions.exception import SessionRetrieveException


class PersistCookies:
    def __init__(self, redis_session, client_id):
        self.redis_session = redis_session
        self.client_id = client_id

    def save_session(self, session, csrf_token=None, form_date=None, headers=None, additional_data=None, timeout=540):
        try:
            cookies = session.cookies._cookies
        except:
            cookies = session
        session_dict = {
            'cookies': cookies,
            'csrf_token': csrf_token,
            'form_date': form_date,
            'headers': headers,
            "additional_data": additional_data
        }
        self.redis_session.setex(self.client_id, timeout, jsonpickle.encode(session_dict))

    '''
    Default argument is given,
    so that there is no need to pass empty session object,
    when we only need headers and not session from redis
    '''

    def load_session(self, session=Session()):
        try:
            session_json = self.redis_session.get(self.client_id).decode('utf-8')
        except Exception as e:
            logging.exception(e)
            raise SessionRetrieveException
        if session_json:
            session_dict = jsonpickle.decode(session_json)
            try:
                if session_dict['cookies']:
                    jar = RequestsCookieJar()
                    jar._cookies = session_dict['cookies']
                    session.cookies = jar
                    return session_dict
                return session_dict
            except KeyError as e:
                print(e)
                return False
        else:
            return False

    def unset_session(self):
        self.redis_session.delete(self.client_id)
