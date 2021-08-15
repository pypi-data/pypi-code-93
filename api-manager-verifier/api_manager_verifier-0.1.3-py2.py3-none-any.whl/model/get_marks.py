class GetMarksApplicant:

    def __init__(self):
        super(GetMarksApplicant).__init__()
        self.roll=None
        self.scl_code=None

    @classmethod
    def applicant_to_object(cls,db_ob):
        applicant = cls()
        applicant.roll=db_ob.roll
        applicant.scl_code=db_ob.scl_code
        return applicant