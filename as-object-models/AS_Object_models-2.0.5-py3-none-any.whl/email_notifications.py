from .utils import FireStoreBase
from datetime import datetime
import jmespath
import logging

from .utils import Email

class EmailNotifications(FireStoreBase):

    ext_fields = ['email_type','active','sender','receive','parent_path','path']
    COLLECTION_NAME = 'application_data'
    logger = logging.getLogger("EmailNotifications")
    
    def __init__(self, fsClient, **kwargs):
        self.email_type = kwargs.get('email_type','') #ndb.StringProperty(required=True)
        self.active = kwargs.get('active','') #ndb.BooleanProperty(default=True)
        self.sender = kwargs.get('sender','') #ndb.StringProperty(required=True)
        self.receive = kwargs.get('receive','') #ndb.StringProperty(repeated=True)
        super(EmailNotifications, self).__init__(fsClient, **kwargs)

    def base_path(self):
        return EmailNotifications.__basePath(self._fsClient)

    @classmethod
    def basePath(cls):
        return EmailNotifications.__basePath(EmailNotifications.get_client())

    @classmethod
    def __basePath(cls,inClient):
        return EmailNotifications.COLLECTION_NAME+'/'+inClient.company+'/Sales_Inventory/Converted/EmailNotifications'

    @classmethod
    def getInstance(cls,fsDocument):
        ref,snap = EmailNotifications.getDocuments(fsDocument)
        docDict = snap.to_dict() if snap.exists else {}
        docDict['fs_docSnap'] = snap
        docDict['fs_docRef'] = ref
        return EmailNotifications(EmailNotifications.get_firestore_client(),**docDict)
    

    @classmethod
    def get_active(cls):
        return EmailNotifications.get_active_any(EmailNotifications.get_firestore_client,EmailNotifications.basePath,EmailNotifications)

    def get_schema(self):
        schema = self.get_bq_schema()
        schema['fields'].append({'field_name':'email_type','field_type':'string'})
        schema['fields'].append({'field_name':'active','field_type':'boolean'})
        schema['fields'].append({'field_name':'sender','field_type':'string'})
        schema['fields'].append({'field_name':'receive','field_type':'string'})
        return schema

    def get_values_dict(self):
        values = self.get_dict()
        values['email_type'] = self.email_type
        values['active'] = self.active
        values['sender'] = self.sender
        values['receive'] = self.receive
        return values

    def send_an_email(self,email_subject, message):
        em = Email()
        em.sender = self.sender
        em.subject = email_subject
        em.body = message
        em.receivers = self.receive if isinstance(self.receive,list) else [self.receive]
        em.send()

    @classmethod
    def _get_email(cls,email_type):
        col = EmailNotifications.get_firestore_client().collection(EmailNotifications.basePath())
        itr = col.where("email_type","==",email_type).stream()
        emls = [EmailNotifications.getInstance(snap) for snap in itr]
        if emls and len(emls) > 0:
            return emls
        return None

    @classmethod
    def send_test_email(cls):
        emls = EmailNotifications._get_email("test")

        if not emls or len(emls) == 0:
            d = {"email_type":'test',"active":True,"sender":"system@analyticssupply",
                 "receive":[EmailNotifications.get_client().user_email]}

            test_email = EmailNotifications(EmailNotifications.get_firestore_client(),**d)

            test_email.update_ndb()
        

        EmailNotifications.send_email("test", "Testing the Email Feature", "This is just a test")


    @classmethod
    def send_email(cls, email_type, email_subject, message):
        ens = EmailNotifications._get_email(email_type)
        if ens:
            for en in ens:
                if en.active and not en.soft_delete:
                    en.send_an_email(email_subject,message)
        else:
            EmailNotifications.logger.warning("No Email Setup for this type: {}".format(email_type))
            EmailNotifications.logger.warning(email_subject)
            EmailNotifications.logger.warning(message)