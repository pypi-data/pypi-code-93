from lxml import etree
from requests import session, codes
from requests.exceptions import Timeout, ConnectionError
from cumsdtu.exceptions.exception import VerifierRequestException

class BaseResposne:
    headers = dict()
    common_params = None
    pre_query_url = None
    query_url = None
    pre = False
    applicant_class = None
    rules = {

    }
    timeout_setting = {
        "timeout": 1
    }
    number_retries = 10
    proxy_class = 'default'

    def __init__(self, to_verify):
        self.to_verify = to_verify
        self.validity = None
        self.session = self.get_requests_session()

    @classmethod
    def get_requests_session(cls):
        requests_session = session()
        requests_session.headers.update(cls.headers)

        return requests_session

    def smart_request(self, type_of_request, url, **kwargs):
        count = 0
        number_retries = kwargs.pop('number_retries', None)
        updated_kwargs = {**self.timeout_setting, **kwargs}
        if number_retries is None:
            number_retries = self.number_retries
        while count < number_retries:
            try:
                if type_of_request == 'GET':
                    response = self.session.get(url, **updated_kwargs)
                elif type_of_request == 'POST':
                    response = self.session.post(url, **updated_kwargs)
                else:
                    raise NotImplementedError
                return response
            except Timeout:
                count += 1
                print('Timeout Happened')
                continue
            except ConnectionError as e:
                print(e)
                count += 0.1
                print('Timeout Happened')
                continue
        else:
            raise VerifierRequestException

    # @classmethod
    # def get_html_session(cls):
    #     html_session = HTMLSession()
    #     html_session.headers.update(cls.headers)
    #     return html_session

    @staticmethod
    def get_etree(response):
        if hasattr(response, 'content'):
            tree = etree.HTML(response.content)
        else:
            tree = etree.HTML(response)
        return tree

    @staticmethod
    def get_xml_tree(response):
        if hasattr(response, 'content'):
            tree = etree.XML(response.content)
        else:
            tree = etree.XML(response)
        return tree

    @staticmethod
    def request_ok(status_code):
        return status_code == codes.ok

    def pre_query(self):
        pass

    def query_info(self, **kwargs):
        pass

    def extract_info(self, response):
        pass

    def verify_info(self, **kwargs):
        pass

    @classmethod
    def verify(cls, db_ob, **_kwargs):
        applicant = cls.applicant_class.object_to_applicant(db_ob)
        if cls.pre:
            return cls(applicant).pre_query()
        else:
            return cls(applicant).query_info()

    @classmethod
    def get_hidden_payload(cls, response):
        tree = cls.get_etree(response)
        hidden_inputs = tree.xpath("//form//input[@type='hidden']")
        hidden_payload = {x.attrib.get('name'): x.attrib.get('value') for x in hidden_inputs}
        return hidden_payload