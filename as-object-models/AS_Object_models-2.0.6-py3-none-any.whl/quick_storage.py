from .utils import FireStoreBase
from datetime import datetime

class QuickStorage(FireStoreBase):
    '''
    Found there are limitations to memcache... so we're creating a quickstorage... basically..
    if we want to return a lot of data... that exists in multiple places.. we'll store it here as a key/value pair
    '''
    COLLECTION_NAME = 'quick_storage'
    ext_fields = ['qsKey','qsValue','qsMinsAlive','qsTimeSet','qsNeverExpire']
    
    def __init__(self,fsClient, **kwargs):
        self.qsKey = kwargs.get('qsKey','--nokey--') #ndb.StringProperty()
        self.qsValue = kwargs.get('qsValue','') #ndb.BlobProperty()
        self.qsMinsAlive = kwargs.get('qsMinsAlive',60)
        self.qsMinsAlive = int(self.qsMinsAlive)
        self.qsTimeSet = kwargs.get('qsTimeSet',datetime.now().isoformat())
        self.qsNeverExpire = kwargs.get('qsNeverExpire',False)
        super(QuickStorage,self).__init__(fsClient,**kwargs)

    def base_path(self):
        return QuickStorage.__basePath(self._fsClient)

    @classmethod
    def get_application_path(cls,application_name=None):
        if application_name is None:
            return cls.basePath()
        else:
            client = cls.get_client()
            return f'{cls.COLLECTION_NAME}/{client.company}/{application_name}'


    @classmethod
    def basePath(cls):
        return cls.__basePath(cls.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return cls.COLLECTION_NAME+'/'+inClient.company+'/'+inClient.application

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = cls.getDocuments(fsDocument)
        docDict = cls.snapToDict(snap)
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return cls(cls.get_client(),**docDict)

    @classmethod
    def __get_qs(cls,inKey, application=None):
        qs = cls.getInstance(cls.get_firestore_client().document(cls.get_application_path(application_name=application)+'/'+inKey))
        if qs.exists:
            setTime = datetime.fromisoformat(qs.qsTimeSet)
            diffMins = (datetime.now() - setTime).total_seconds() / 60.0
            if diffMins > qs.qsMinsAlive and not qs.qsNeverExpire:
                qs.reference.delete()
                return None
            else:
                return qs
        return None

    @classmethod
    def getValue(cls,inKey, application=None):
        '''
        :param inKey: string value
        :return: string value
        '''
        qs = cls.__get_qs(inKey,application=application)
        if qs:
            return qs.qsValue
        return None

    @classmethod
    def deleteValue(cls,inKey,application=None):
        '''
        :param inKey: string value
        '''
        qs = cls.getInstance(cls.get_firestore_client().document(cls.get_application_path(application_name=application)+'/'+inKey))
        if qs.exists:
            qs.reference.delete()

    @classmethod
    def setValue(cls,inKey, inValue, expireMins=None, neverExpire=False,application=None):
        '''
        :param inKey: string value...
        :param inValue: should be of type dict... it will be converted to a string
        :param expireMins:  how long should this value be stored (default is 60 mins)
        :return:  nada
        '''
        qs = cls.__get_qs(inKey,application=application)
        if qs:
            qs.qsValue = inValue
            qs.qsNeverExpire = neverExpire
            if expireMins:
                qs.qsMinsAlive = expireMins
        else:
            data = {}
            clt = cls.get_client()
            data['qsKey'] = inKey
            data['qsValue'] = inValue
            data['qsNeverExpire'] = neverExpire
            if expireMins:
                data['qsMinsAlive'] = expireMins
            data['fs_docRef'] = clt.fsClient.document(cls.get_application_path(application_name=application)+'/'+inKey)
            qs = QuickStorage(clt.fsClient,**data)

        qs.update_ndb()