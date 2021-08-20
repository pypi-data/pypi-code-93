from .utils import FireStoreBase
from .data_storage_type import DataStorageType

class ReportingConfig(FireStoreBase):

    COLLECTION_NAME = 'reporting_config'
    ext_fields = ['name','reportingOn']

    def __init__(self,fsClient,**kwargs):
        self.name = kwargs.get('name','') #ndb.StringProperty(required=True) # This will be the DataStorageType
        self.reportingOn = kwargs.get('reportingOn','') #ndb.BooleanProperty(default=True)
        super(ReportingConfig,self).__init__(fsClient,**kwargs)
    
    def base_path(self):
        return ReportingConfig.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return ReportingConfig.__basePath(ReportingConfig.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return ReportingConfig.COLLECTION_NAME+'/'+inClient.company+'/'+inClient.application


    @classmethod
    def get_reporting(cls, report_name):
        clt = ReportingConfig.get_client()
        docRef = clt.fsClient.document(ReportingConfig.basePath()+'/'+report_name)
        docRef,snap = cls.getDocuments(docRef)
        if not snap.exists:
            data = {}
            data['name'] = report_name
            data['reportingOn'] = True
            data['fs_docRef'] = docRef
            data['fs_docSnap'] = snap
            lstUp = ReportingConfig(clt.fsClient,**data)       
            lstUp.update_ndb()
            return lstUp
        data = snap.to_dict()
        data['fs_docRef'] = docRef
        data['fs_docSnap'] = snap
        return ReportingConfig(clt.fsClient,**data)

    @classmethod
    def isReportingOn(cls, report_name):
        rptConfig = ReportingConfig.get_reporting(report_name)
        return rptConfig.reportingOn if rptConfig is not None else False

    @classmethod
    def getAllReporting(cls):
        '''
        Query all of DataStorageType and return a list of the ones that have reporting turned on..

        Boom!
        '''
        reporting = []
        lst = DataStorageType.getAll_DSTNames()
        for dstName in lst:
            rptC = ReportingConfig.get_reporting(dstName)
            if rptC.reportingOn:
                reporting.append(rptC.name)

        return reporting

    def turn_on(self):
        self.reportingOn = True
        self.update_ndb()

    def turn_off(self):
        self.reportingOn = False
        self.update_ndb()
