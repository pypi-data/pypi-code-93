import redis

from cumsdtu.model.lsa_model import ManageSubjectSelection
from cumsdtu.lsa_academy.logins.login import Login
from cumsdtu.utils.persist_cookies import PersistCookies

class CourseDetail(Login):

    applicant_class = ManageSubjectSelection

    selection_url="https://cumsdtu.in/LSARegistration/api/getSubjDtls?instId=1&subjId={}&stuId={}&esetId={}"

    INSIGNIFICANT_KEYS=['courseDependencies','courseType','courseUrl','isFacultyRequired','isOpenElective','minimumCourseCredit',
                        'applied','dayPrdSectionDtlMp','instructorName','registered','roomNo','sectionId','sectionName','strength',
                        'title','session']

    def __init__(self, to_verify, **kwargs):
        super().__init__(to_verify, **kwargs)
        self.to_verify=to_verify
        self.persistor=self.safe_dict(kwargs,'persistor')
        self.student_id = self.safe_dict(kwargs,'student_id')
        self.check_course_exist=self.safe_dict(kwargs,'check_course_exist',False)

    def pre_query(self):

        result=self.find_subject_details(self.to_verify.set_code,self.to_verify.subject_id)

        if result.get('error'):
            return result

        response=self.smart_request('GET',self.selection_url.format(self.to_verify.subject_id,self.student_id,result.get('esetId')),
                           headers=self.headers)

        json_data=self.safe_json(response.text)

        if json_data.get('error'):
            return self.custom_response(json_data.get('error'),json_data.get('msgLst'),422)

        details=json_data.pop('data')
        self.pop_insignificant_keys(details)

        if not self.check_course_exist:
            return self.custom_response(False,"Success",200,data=details)
        else:
            return self.custom_response(False,"Course Exist",200)
    @classmethod
    def extract_data(cls, db_ob, **kwargs):
        applicant = cls.applicant_class.applicant_to_object(db_ob)

        login_data=Login.do_login(applicant,**kwargs)

        if login_data.get('status')!=200:
            return login_data

        return cls(applicant,**{**login_data.pop('data'),**login_data, **kwargs}).pre_query()


def test():
    applicant = ManageSubjectSelection()
    applicant.username = '2K19/ME/051'
    applicant.password = 'April@2000'
    applicant.set_code = 'B'
    applicant.subject_id = 2607

    # r = redis.Redis(host='redis-13748.c14.us-east-1-2.ec2.cloud.redislabs.com',
    #                 port=13748,
    #                 password='KfhZsGRLZ0aqDzT4pl1K4BmfrFbrpaGn')

    r = redis.StrictRedis()

    persistor = PersistCookies(r, 'cumsdtu:{}'.format(applicant.username.replace('/', '_')))

    return CourseDetail.extract_data(applicant,persistor=persistor)


if __name__ == '__main__':
    print(test())