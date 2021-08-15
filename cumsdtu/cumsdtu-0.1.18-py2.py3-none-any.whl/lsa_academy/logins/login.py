import re
import os
import ast
import json
import redis
import logging
import pandas as pd

from collections.abc import Sequence
from cumsdtu.base import BaseResposne
from collections.abc import MutableMapping
from cumsdtu.utils.utils import EncryptDecrypt
from cumsdtu.model.lsa_model import ManageCredentials
from cumsdtu.templates.template import login_template
from cumsdtu.utils.persist_cookies import PersistCookies
from cumsdtu.exceptions.exception import BackendError, SessionRetrieveException


class Login(BaseResposne):
    base_url = "https://cumsdtu.in/registration_student/login/login.jsp?courseRegistration"
    login_url = "https://cumsdtu.in/registration_student/LoginServlet"
    check_credentails = 'https://cumsdtu.in/LSARegistration/getStudent?stuId={}'
    reg_details = 'https://cumsdtu.in/LSARegistration/api/getStuRegistration?stuId={}&instId=1'

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
    INSIGNIFICANT_KEYS = ['extraValueMap', 'helperData', 'nextStageId', 'paymentDescription', 'saveDeleteRecord',
                          'sessionId', 'showSpecializations',
                          'maximumRegistrationCredit', 'minimumRegistrationCredit', 'registrationNo',
                          'registrationRoundNo',
                          'specialization1', 'specialization2', 'totalAmount', 'creditsRegistered',
                          'electiveCoursesList',
                          'choiceType', 'countVisible', 'credits',
                          'creditsTypeChoice',
                          'extraValueMap', 'registrationRoundNo', 'registrationNo',
                          'gradeId', 'headerFlag', 'minimumSeats', 'numChoice', 'orgStageId',
                          'prevSubjId', 'resultStatus', 'seats',
                          'subHeader2Flag', 'subHeaderFlag', 'substitutedCourseId', 'substitutedCourseLabel', 'waitListed']
    maps = ['courseCode', 'courseGroupLabel', 'courseId', 'courseName', 'registrationCount', 'totalSeats',
            'registeredFlag', 'disabledFlag']
    heading = ['Course Code', 'Course Group Name', 'Course Id', 'Course Name', 'Seats Registered',
               'Total Seats', 'Is Registered', 'Disabled']

    applicant_class = ManageCredentials

    def __init__(self, to_verify, **kwargs):
        super().__init__(to_verify)
        self.to_verify = to_verify
        self.reg_data = self.safe_dict(kwargs, 'reg_data')
        self.student_id = self.safe_dict(kwargs, 'student_id')
        self.persistor = self.safe_dict(kwargs, 'persistor')
        self.file_name = self.safe_dict(kwargs, 'file_name')
        self.show_reg_courses = self.safe_dict(kwargs, 'show_courses')
        self.course_detail = self.safe_dict(kwargs, 'course_detail')
        self.auth_session = self.safe_dict(kwargs, 'session_auth_key')
        self.check_exist = self.safe_dict(kwargs, 'check_exist', False)

    def safe_dict(self, data: dict, key, default=None):
        try:
            return data.get(key)
        except KeyError:
            return default

    def safe_json(self, data: str):

        if data.__contains__('Down for Maintenance'):
             return self.custom_response(True,"Website is Down for Maintenance",503)

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logging.exception("Error decoding data ")
            print(data)
            raise BackendError

    def find_msg(cls, text)->str:

        if text is None:
            return ''

        data = re.findall(r'>.+<', text)
        if len(data) > 0:
            return data[0][1:-1]
        else:
            return text

    def custom_response(self, *args, **kwargs):
        response = {
            'error': args[0] if isinstance(args[0], bool) else ast.literal_eval(str(args[0]).capitalize()),
            'msgLst': args[1] if not isinstance(args[1],list) else args[1][-1].get('errCode'),
            'status': args[2],
            **kwargs
        }

        return response

    def map_nested_keys(self, mapping, function):
        for key in list(mapping):
            try:
                value = mapping[key]
            except KeyError:
                continue
            if isinstance(value, MutableMapping):
                self.map_nested_keys(value, function)
            if isinstance(value, Sequence):
                [self.map_nested_keys(m, function) for m in value if isinstance(m, MutableMapping)]
            function(mapping, key)

    def pop_insignificant_keys(self, data):
        return self.map_nested_keys(
            data, lambda dict_, key: dict_.pop(key, None) if key in self.INSIGNIFICANT_KEYS else None
        )

    def find_subject_details(self, set_data, sub_code):

        details = self.filter_course_list(self.course_detail, False)
        data = self.safe_dict(details, set_data)
        if data is None:
            return self.custom_response(True, "Invalid Course set/Group", 422)

        for i in data:
            if i.get('courseId') == sub_code:
                return self.custom_response(False, "Success", 200, **i)

        return self.custom_response(True, "Course Id not found", 422)

    def safe_list(self,list,index,default=''):
        try:
            return list[index]
        except IndexError:
            return default

    def save_session(self, additional_data):
        self.persistor.save_session(self.session, additional_data=additional_data,
                                    timeout=self.DEFAULT_PERSISTOR_EXPIRY)

    def load_sess(self):
        try:
            return self.persistor.load_session(self.session)
        except SessionRetrieveException:
            return False

    def check_registered(self, result: dict):
        reg_course = self.reg_data['coreCoursesList']
        for i in reg_course:
            if i.get('courseId') == result.get('courseId') and i.get('esetId') == result.get('esetId'):
                return self.custom_response(False, "Course Already Registered", 1, course_id=result.get('courseId'),
                                            eset_id=result.get('esetId'))

        return self.custom_response(False, "Course Not registered", 0, course_id=result.get('courseId'),
                                    eset_id=result.get('esetId'), facultyName=result.get('facultyName'))

    def course_details_filter(self, data: dict, filter_key=True):

        if filter_key:
            return {self.heading[i]: data.get(self.maps[i]) for i in range(len(self.maps))}
        else:
            return {self.heading[i].lower().replace(' ', '_'): data.get(self.maps[i]) for i in range(len(self.maps))}

    def filter_course_list(self, data: list, filter_course_items=True, filter_keys=True):
        new_dict = dict()
        for i in data:
            if i.get('courseId') is not None:
                try:
                    # if len(i.get('courseGroupLabel'))>0 else str(i.get('courseGroupId'))
                    new_dict[i.get('courseGroupLabel')].append(
                        self.course_details_filter(i, filter_keys) if filter_course_items else i)
                except KeyError:
                    new_dict[i.get('courseGroupLabel')] = [
                        self.course_details_filter(i, filter_keys) if filter_course_items else i]

        return new_dict

    def conversion_for_xlmx(self, data: dict):
        value = dict()
        for i in data.keys():
            for j in data.get(i):
                for items in self.heading:
                    try:
                        value[items].append(j.get(items))
                    except KeyError:
                        value[items] = [j.get(items)]

        return value

    def write_data(self, data: list, file_name: str):

        if os.path.exists(file_name):
            os.remove(file_name)

        if file_name.endswith('.json'):
            data = self.filter_course_list(data, filter_keys=False)
            file = open(file_name, 'w')
            file.write(str(json.dumps(data, indent=4, sort_keys=True)))
            file.close()

        if file_name.endswith('.xlsx'):
            data = self.filter_course_list(data)
            json_data = self.conversion_for_xlmx(data)
            df = pd.DataFrame(json_data)
            df.to_excel(file_name)

    def pre_query(self):
        respose = self.smart_request('GET', self.base_url, headers=self.headers)
        hidden_payload = self.get_hidden_payload(respose)
        if hidden_payload.get(None) is None:
           if self.safe_list(self.get_etree(respose).xpath('//*[@id="page"]/header/h1//text()'),0).__contains__('Down for Maintenance'):
                return self.custom_response(True,"Website is Down for Maintenance",503)
           else:
               return self.custom_response(True,"Website not responding",503)

        return self.query_info(salt=hidden_payload.get(None))

    def query_info(self, **kwargs):
        self.headers['Referer'] = 'https://cumsdtu.in/registration_student/login/login.jsp?courseRegistration'
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'

        enc_pass = EncryptDecrypt.enc_sha256(self.to_verify.password + kwargs['salt'])
        payload = login_template(self.to_verify.username, enc_pass)

        respose = self.smart_request('POST', self.login_url, data=payload, headers=self.headers, allow_redirects=False)

        try:
            data = respose.headers['Location'].split('regId=')[1]

            if not data.endswith('==') or len(data) < 24:
                raise IndexError

            self.student_id = data
        except IndexError:
            return self.custom_response(True, "Invalid Username or Password", 409)

        self.headers['Referer'] = respose.headers['Location']

        return self.check_login_status()

    def check_login_status(self):
        response = self.smart_request('GET', self.check_credentails.format(self.student_id), headers=self.headers)

        json_data = self.safe_json(response.text)

        if json_data['error']:
            return self.custom_response(json_data.get('error'), json_data.get('msgLst'), 422)

        if self.check_exist:
            maps = ['studentId', 'studentName', 'disciplineName', 'programName', 'stageId']
            data = {i: json_data['data'].get(i) for i in maps}
            return self.custom_response(json_data.get('error'), "Credentails verified successful", 200, data=data)

        self.headers['Authorization'] = json_data.get('session')
        self.auth_session = json_data.get('session')

        additional_data = {"session_auth_key": self.auth_session, "student_id": self.student_id}
        self.save_session(additional_data=additional_data)

        return self.extract_info(data=additional_data)

    def extract_info(self, **kwargs):
        response = self.smart_request('GET', self.reg_details.format(self.student_id), headers=self.headers)

        if response.status_code == 401:
            return self.custom_response(True, 'UnAuthorized User', 401)

        self.reg_data = self.safe_json(response.text)

        self.course_detail = self.reg_data['data']['electiveCoursesList']

        if self.file_name is not None:
            # self.to_verify.username.replace('/','_')+'.xlsx'
            self.write_data(self.course_detail, self.file_name)
            return self.custom_response(False, "Course details written to {} successfully".format(self.file_name), 200,
                                        extra_info=self.reg_data.get('data').get('extraInfo'))

        self.pop_insignificant_keys(self.reg_data)

        if self.show_reg_courses:
            return self.custom_response(False, 'Success', 200, data=self.reg_data['data'].get('coreCoursesList'))

        return self.custom_response(False, "Course Details retrived", 200,
                                    **{'reg_data': self.reg_data.get('data'), 'course_detail': self.course_detail,
                                       'extra_info':self.reg_data.get('data').get('extraInfo'),
                                       **kwargs})

    def check_previous_session(self):
        session_storage = self.load_sess()
        if not isinstance(session_storage, bool):
            try:
                self.headers['Authorization'] = session_storage['additional_data']['session_auth_key']
                self.student_id = session_storage['additional_data']['student_id']
            except Exception:
                return False,''


            response = self.extract_info(data=session_storage['additional_data'])
            if response.get('status') == 200:
                return True, response

        return False, {}

    @classmethod
    def do_login(cls, db_ob, **kwargs):
        applicant = cls.applicant_class.applicant_to_object(db_ob)

        obj = cls(applicant, **kwargs)

        if not obj.check_exist:
            status, response = obj.check_previous_session()
        else:
            status, response = False, None
        # status,response = False,{}
        if not status:
            return obj.pre_query()
        else:
            return response


def test():
    applicant = ManageCredentials()
    applicant.username = '2K19/ME/051'
    applicant.password = EncryptDecrypt.enc_sha1('April@2000')

    # r=redis.Redis(host='redis-13748.c14.us-east-1-2.ec2.cloud.redislabs.com',
    #               port=13748,
    #               password='KfhZsGRLZ0aqDzT4pl1K4BmfrFbrpaGn')

    r = redis.StrictRedis()

    persistor = PersistCookies(r, 'cumsdtu:{}'.format(applicant.username.replace('/', '_')))

    return Login.do_login(applicant, persistor=persistor)


if __name__ == '__main__':
    print(test())
