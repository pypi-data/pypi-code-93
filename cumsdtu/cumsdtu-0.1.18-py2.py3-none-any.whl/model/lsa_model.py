class ManageCredentials:

    def __init__(self):
        super(ManageCredentials).__init__()
        self.username=None
        self.password=None

    @classmethod
    def applicant_to_object(cls,db_ob):
        applicant = cls()
        applicant.username=db_ob.username
        applicant.password=db_ob.password
        return applicant

class ManageSubjectSelection:

    def __init__(self):
        super(ManageSubjectSelection).__init__()
        self.username=None
        self.password=None
        self.set_code=None
        self._subject_id=None

    @classmethod
    def applicant_to_object(cls,db_ob):
        applicant = cls()
        applicant.username=db_ob.username
        applicant.password=db_ob.password
        applicant.set_code=db_ob.set_code
        applicant._subject_id=db_ob.subject_id
        return applicant

    @property
    def subject_id(self):
        return self._subject_id

    @subject_id.setter
    def subject_id(self,value):
        try:
            self._subject_id=int(value)
        except ValueError:
            raise ValueError("Required Integer, provided {}".format(value))

class ManageForgotPassword:

    def __init__(self):
        super(ManageForgotPassword).__init__()
        self.username=None
        self.new_password=None
        self.mobile=None
        self.email=None
        self.otp=None

    @classmethod
    def applicant_to_object(cls,db_ob):
        applicant = cls()
        applicant.username=db_ob.username
        applicant.new_password=db_ob.new_password
        applicant.mobile=db_ob.mobile
        applicant.email=db_ob.email
        applicant.otp=db_ob.otp

        return applicant
