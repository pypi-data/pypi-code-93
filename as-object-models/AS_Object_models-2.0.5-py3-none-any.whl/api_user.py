from .utils import FireStoreBase
from .quick_storage import QuickStorage

import uuid,logging

class ApiUser(FireStoreBase):

    ext_fields = ['userName','userPass']
    COLLECTION_NAME = 'application_data'

    def __init__(self,fsClient, **kwargs):
        self.userName = kwargs.get('userName','') #ndb.StringProperty(default="admin")
        self.userPass = kwargs.get('userPass','') #ndb.StringProperty(default="admin")
        super(ApiUser,self).__init__(fsClient,**kwargs)

    
    def base_path(self):
        return ApiUser.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return ApiUser.__basePath(ApiUser.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return ApiUser.COLLECTION_NAME+'/'+inClient.company+'/Data_API'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = cls.getDocuments(fsDocument)
        docDict = {'userName':'','userPass':''}
        if snap.exists:
            docDict = snap.to_dict()

        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return cls(cls.get_firestore_client(),**docDict)

    @classmethod
    def createUser(cls,userName,userPass):
        user = ApiUser.getFirst(userName)
        if not user.exists:
            user.userName = userName
            user.userPass = userPass
            #user = ApiUser(userName = userName, userPass=userPass)
            user.update_ndb()
        return user

    @classmethod
    def deleteUser(cls,userName):
        user = ApiUser.getFirst(userName)
        if user.exists:
            user.reference.delete()

    @classmethod
    def getUsers(cls):
        userList = []
        users = ApiUser.get_firestore_client().collection(ApiUser.basePath()).list_documents()
        for userRef in users:
            userDb = ApiUser.getInstance(userRef)
            user = userDb.get_dict()
            userList.append({'userName': user['userName'], 'userPass': user['userPass']})

        return userList

    @classmethod
    def getFirst(cls,userName):
        #users = ApiUser.query(ApiUser.userName == userName).fetch()
        userRef = ApiUser.get_firestore_client().document(ApiUser.basePath()+'/'+userName)
        return ApiUser.getInstance(userRef)

    @classmethod
    def updateUserPass(cls,userName,userPass):
        user = ApiUser.getFirst(userName)
        if not user.exists:
            user = ApiUser.createUser(userName,userPass)

        user.userPass = userPass
        user.update_ndb
        return user

    @classmethod
    def validateUser(cls,userName,userPass):
        user = ApiUser.getFirst(userName)
        if not user.exists:
            return False

        if user.userPass == userPass:
            return True

        return False

    @classmethod
    def getToken(cls,userName,userPass):
        if ApiUser.validateUser(userName, userPass):
            token = QuickStorage.getValue(userName)
            if not token:
                token = userName + "|" + str(uuid.uuid4())
                #memcache.set(userName, token, DEFAULT_CACHE_TIME)
                QuickStorage.setValue(userName,token)

        #if ApiUser.validateUser(userName,userPass):
        #    token = userName+"|"+str(uuid.uuid4())
        #    memcache.set(userName,token,DEFAULT_CACHE_TIME)
            return token
        return None

    @classmethod
    def getInternalApiToken(cls):
        user_name = 'internal_api'
        token = QuickStorage.getValue(user_name)
        if token:
            return token

        token = user_name + "|" + str(uuid.uuid4())
        QuickStorage.setValue(user_name, token)
        return token

    @classmethod
    def validateToken(cls,inToken):
        userName = inToken.split("|")[0]
        token = QuickStorage.getValue(userName)
        if token == inToken:
            return True
        logging.error("Could not validate user: {}, with token: {}".format(userName, inToken))
        return False