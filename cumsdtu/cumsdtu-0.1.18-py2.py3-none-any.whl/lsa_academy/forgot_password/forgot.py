import ast
import json
import redis
import logging

from cumsdtu.base import BaseResposne
from cumsdtu.utils.utils import EncryptDecrypt
from cumsdtu.utils.persist_cookies import PersistCookies
from cumsdtu.model.lsa_model import ManageForgotPassword
from cumsdtu.exceptions.exception import BackendError,SessionRetrieveException
from cumsdtu.templates.template import forgot_password_submit_username,forgot_pass_submit_otp,\
    forgot_pass_submit_phone_email,submit_new_password

class GenerateOTP(BaseResposne):

    base_url = "https://cumsdtu.in/registration_student/login/login.jsp?courseRegistration"
    forgot_password_url='https://cumsdtu.in/registration_student/ForgotPassServlet'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,vi;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'cumsdtu.in',
        'Pragma': 'no-cache',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    DEFAULT_PERSISTOR_EXPIRY = 60 * 60
    applicant_class = ManageForgotPassword

    def __init__(self,to_verify,**kwargs):
        super().__init__(to_verify)
        self.to_verify=to_verify
        self.persistor = kwargs.get('persistor')
        self.do_need_help=kwargs.get("need_help",False)

    def safe_json(self, data: str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logging.exception("Error decoding data ")
            print(data)
            raise BackendError

    def check_error(self,data:dict):
        try:
            return data['error']
        except KeyError:
            return None

    def custom_response(self, *args, **kwargs):
        response = {
            'error': args[0] if isinstance(args[0], bool) else ast.literal_eval(str(args[0]).capitalize()),
            'msgLst': args[1] if not isinstance(args[1],list) else args[1][-1].get('errCode'),
            'status': args[2],
            **kwargs
        }
        return response

    def save_session(self, additional_data):
        self.persistor.save_session(self.session, additional_data=additional_data,
                                    timeout=self.DEFAULT_PERSISTOR_EXPIRY)

    def pre_query(self):
        _=self.smart_request('GET',self.base_url,headers=self.headers)

        return self.query_info()

    def query_info(self, **kwargs):
        payload = forgot_password_submit_username(self.to_verify.username)
        response = self.smart_request('POST',self.forgot_password_url,data=payload,headers=self.headers)

        json_data=self.safe_json(response.text)

        if self.check_error(json_data) is not None:
            return self.custom_response(True,self.check_error(json_data),409)

        if self.do_need_help:
            return self.custom_response(False,json_data.pop('success'),200,**json_data)

        return self.submit_details()

    def submit_details(self):
        payload =forgot_pass_submit_phone_email(self.to_verify.username,self.to_verify.mobile,self.to_verify.email)
        response = self.smart_request('POST',self.forgot_password_url,data=payload,headers=self.headers)

        json_data=self.safe_json(response.text)

        if self.check_error(json_data) is not None:
            return self.custom_response(True,self.check_error(json_data),400)

        self.save_session(None)

        return self.custom_response(False,json_data.get("success"),200)

    @classmethod
    def extract_data(cls, db_ob, **kwargs):
        applicant = cls.applicant_class.applicant_to_object(db_ob)

        return cls(applicant, **kwargs).pre_query()


class SubmitOTP(GenerateOTP):

    def __init__(self,to_verify,**kwargs):
        super().__init__(to_verify,**kwargs)
        self.to_verify=to_verify
        self.persistor=kwargs.get('persistor')

        self.load_sess()

    def load_sess(self):
        try:
            return self.persistor.load_session(self.session)
        except SessionRetrieveException:
            return False

    def submit_otp(self):
        payload = forgot_pass_submit_otp(self.to_verify.username,self.to_verify.otp)
        response = self.smart_request('POST',self.forgot_password_url,data=payload,headers=self.headers)

        json_data=self.safe_json(response.text)

        if self.check_error(json_data) is not None:
            return self.custom_response(True,self.check_error(json_data),409)

        rsa_key=json_data.get('rsa_key')
        return self.submit_new_pass(rsa_key=rsa_key)

    def submit_new_pass(self, **kwargs):
        payload = submit_new_password(self.to_verify.username,EncryptDecrypt.rsa_enc(kwargs.get('rsa_key'),self.to_verify.new_password))
        response=self.smart_request('POST',self.forgot_password_url,data=payload,headers=self.headers)

        json_data=self.safe_json(response.text)

        if self.check_error(json_data) is not None:
            return self.custom_response(True,self.check_error(json_data),409)

        return self.custom_response(False,json_data.pop("success"),200,**json_data)

    @classmethod
    def extract_data(cls, db_ob, **kwargs):
        applicant = cls.applicant_class.applicant_to_object(db_ob)

        return cls(applicant, **kwargs).submit_otp()


def test():
    applicant = ManageForgotPassword()
    applicant.username = '2K19/ME/051'
    applicant.mobile=9891472291
    applicant.email='ashishkumar28april@gmail.com'

    r=redis.Redis(host='redis-13748.c14.us-east-1-2.ec2.cloud.redislabs.com',
                  port=13748,
                  password='cumsdtu_c8F-w0ppLGVmLVIPjDLDvw')

    # r = redis.StrictRedis()

    persistor = PersistCookies(r, 'cumsdtu:{}'.format(applicant.username.replace('/', '_')))

    data= GenerateOTP.extract_data(applicant,persistor=persistor)
    print(data)

    applicant.otp = int(input("Enter OTP: "))
    applicant.new_password = EncryptDecrypt.enc_sha1(input("Enter new password"))

    return SubmitOTP.extract_data(applicant,persistor=persistor)

if __name__ == '__main__':
    print(test())