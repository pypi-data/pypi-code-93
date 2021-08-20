from .utils import FireStoreBase
import logging

class AppConfiguration(FireStoreBase):

    COLLECTION_NAME = 'app_configuration'
    ext_fields = ['configuration_name','configuration_number','configuration_description','configuration_url','configuration_data']

    def __init__(self,fsClient,**kwargs):
        self.configuration_name = kwargs.get('configuration_name',None) #ndb.StringProperty(required=True)
        self.configuration_number = kwargs.get('configuration_number',None) #ndb.IntegerProperty(required=True)
        self.configuartion_description = kwargs.get('configuration_description',None) #ndb.TextProperty(required=False)
        self.configuration_url = kwargs.get('configuration_url',None) #ndb.StringProperty(required=False)
        self.configuration_data = kwargs.get('configuration_data',None) #ndb.JsonProperty(required=False)
        super(AppConfiguration,self).__init__(fsClient,**kwargs)

    def base_path(self):
        return AppConfiguration.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return AppConfiguration.__basePath(AppConfiguration.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return AppConfiguration.COLLECTION_NAME+'/'+inClient.company+'/'+inClient.application
         
    def get_document(self,clnt):
        return AppConfiguration.__get_document(clnt,self.base_path(),self.configuration_name,self.configuration_number)
    
    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = cls.getDocuments(fsDocument)
        docDict = snap.to_dict()
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return cls(cls.get_firestore_client(),**docDict)

    @classmethod
    def get_all(cls):
        clt = AppConfiguration.get_client()
        collRef = clt.fsClient.collection(AppConfiguration.__basePath(clt))
        docRefList = collRef.list_documents()
        appCfgList = [AppConfiguration.getInstance(d) for d in docRefList]
        return appCfgList

    @classmethod
    def __get_document(cls,clnt,path,cfgName,cfgNumber):
        doc_path = path+"/"+cfgName + "_" + str(cfgNumber)
        return clnt.fsClient.document(doc_path)


    @classmethod
    def has_been_configured(cls, cfgName, cfgNumber):
        clt = AppConfiguration.get_client()
        docRef = AppConfiguration.__get_document(clt,AppConfiguration.__basePath(clt),cfgName,cfgNumber)
        return docRef.get().exists

    @classmethod
    def add_configuration(cls, cfgName, cfgNumber, cfgDescription="",cfgUrl="",cfgData={}):
        if AppConfiguration.has_been_configured(cfgName, cfgNumber):
            pass
        else:
            cfg = AppConfiguration(AppConfiguration.get_firestore_client(),**{'configuration_name':cfgNumber,
                                                                    'configuration_number':cfgNumber,
                                                                    'configuration_url':cfgUrl,
                                                                    'configuration_description':cfgDescription,
                                                                    'configuration_data':cfgDescription})

            cfg.update_ndb()
            logging.info("ran configuration: "+cfg.configuration_name+"("+str(cfg.configuration_number)+")")

