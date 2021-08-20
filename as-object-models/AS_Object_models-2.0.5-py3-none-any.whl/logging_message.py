from .utils import FireStoreBase
class LoggingMessages(FireStoreBase):
    #message = ndb.TextProperty(required=True)
    #msg_type = ndb.StringProperty()

    ext_fields = ['message','msg_type','parent_path','path']
    COLLECTION_NAME = 'application_data'

    def __init__(self, fsClient, **kwargs):
        self.message = kwargs.get('message','') 
        self.msg_type = kwargs.get('msg_type','') 

        super(LoggingMessages, self).__init__(fsClient, **kwargs)
    
    def base_path(self):
        return LoggingMessages.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return LoggingMessages.__basePath(LoggingMessages.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return LoggingMessages.COLLECTION_NAME+'/'+inClient.company+'/Sales_Inventory/Converted/LoggingMessages'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = LoggingMessages.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return LoggingMessages(LoggingMessages.get_firestore_client(),**docDict)

    def get_schema(self):
        schema = self.get_bq_schema()
        schema['fields'].append({'field_name':'message','field_type':'string'})
        schema['fields'].append({'field_name':'msg_type','field_type':'string'})
        return schema

    def get_values_dict(self):
        values = self.get_dict()
        values['message'] = self.message
        values['msg_type'] = self.msg_type
        return values

    @classmethod
    def get_msg_type(cls, instr):
        if instr.lower().startswith("error"):
            return "ERROR"
        if instr.lower().startswith("warn"):
            return "WARNING"
        if instr.lower().startswith("info"):
            return "INFORMATIONAL"
        return instr

    @classmethod
    def create_log_message(cls, msg, msg_type):
        mType = LoggingMessages.get_msg_type(msg_type)
        data = {'message':msg,'msg_type':mType}
        lm = LoggingMessages(LoggingMessages.get_firestore_client(),**data)
        lm.update_ndb(True)
        return lm