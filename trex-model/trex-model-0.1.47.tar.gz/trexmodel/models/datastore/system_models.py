'''
Created on 20 Apr 2020

@author: jacklok
'''
from trexmodel import conf as model_conf
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
 

class Country(BaseNModel, DictModel):
    cnty_id                 = ndb.IntegerProperty(required=True)
    cnty_code               = ndb.StringProperty(required=True)
    cnty_name               = ndb.StringProperty(required=True)
    locale                  = ndb.StringProperty(required=True)
    gmt                     = ndb.StringProperty(required=True)
    trunk_code              = ndb.StringProperty(required=True)
    
    
class ContactUs(BaseNModel, DictModel):
    contact_name                = ndb.StringProperty(required=True)
    contact_email               = ndb.StringProperty(required=True)
    contact_subject             = ndb.StringProperty(required=False)
    contact_message             = ndb.TextProperty(required=True)
    created_datetime            = ndb.DateTimeProperty(required=True, auto_now=True)
    
    dict_properties = ['contact_name', 'contact_email', 'contact_subject', 'contact_message', 
                       'created_datetime']
    
    @staticmethod
    def create(contact_name, contact_email=None, contact_subject=None, contact_message=None):
        ContactUs(
                contact_name    = contact_name,
                contact_email   = contact_email,
                contact_subject = contact_subject,
                contact_message = contact_message,
                ).put()
                
    @staticmethod
    def list(offset=0, limit=10):
        return ContactUs.query().order(-ContactUs.created_datetime).fetch(offset=offset, limit=limit)    
                
class Feedback(BaseNModel, DictModel):
    name                    = ndb.StringProperty(required=True)
    email                   = ndb.StringProperty(required=True)
    rating                  = ndb.StringProperty(required=True)
    message                 = ndb.TextProperty(required=True)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now=True)
    
    @staticmethod
    def create(name=None, email=None, rating=None, message=None):
        ContactUs(
                name        = name,
                email       = email,
                rating      = rating,
                message     = message,
                ).put()                
        
        
class SentEmail(BaseNModel, DictModel):
    email_id                = ndb.StringProperty(required=True)
    batch_id                = ndb.StringProperty(required=True)
    to                      = ndb.StringProperty(required=True)
    subject                 = ndb.StringProperty(required=True)
    html                    = ndb.StringProperty(required=False) 
    body                    = ndb.StringProperty(required=False)
    sent_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)
    sent_response           = ndb.StringProperty(required=False)
    sent_status             = ndb.BooleanProperty(default=False)
    click_status            = ndb.BooleanProperty(default=False)
    read_status             = ndb.BooleanProperty(default=False)
    open_status             = ndb.BooleanProperty(default=False)
    bounce_status           = ndb.BooleanProperty(default=False)
    spam_status             = ndb.BooleanProperty(default=False)
    block_status            = ndb.BooleanProperty(default=False)
    
    
    @classmethod
    def get_by_email_id(cls, email_id):
        return cls.query(ndb.AND(cls.email_id==email_id)).get()
    
    @classmethod
    def update_sent_status_by_email_id(cls, email_id, sent_status=True):
        sent_email = cls.get_by_email_id(email_id)
        if sent_email:
            sent_email.sent_status = sent_status
            sent_email.put()
            
    @classmethod
    def update_open_status_by_email_id(cls, email_id, open_status=True):
        sent_email = cls.get_by_email_id(email_id)
        if sent_email:
            sent_email.open_status = open_status
            sent_email.put()
            
    @classmethod
    def update_click_status_by_email_id(cls, email_id, click_status=True):
        sent_email = cls.get_by_email_id(email_id)
        if sent_email:
            sent_email.click_status = click_status
            sent_email.put()  
            
    @classmethod
    def update_read_status_by_email_id(cls, email_id, read_status=True):
        sent_email = cls.get_by_email_id(email_id)
        if sent_email:
            sent_email.read_status = read_status
            sent_email.put()          
            
    @classmethod
    def update_bounce_status_by_email_id(cls, email_id, bounce_status=True):
        sent_email = cls.get_by_email_id(email_id)
        if sent_email:
            sent_email.bounce_status = bounce_status
            sent_email.put()  
            
    @classmethod
    def update_spam_status_by_email_id(cls, email_id, spam_status=True):
        sent_email = cls.get_by_email_id(email_id)
        if sent_email:
            sent_email.spam_status = spam_status
            sent_email.put() 
            
    @classmethod
    def update_block_status_by_email_id(cls, email_id, block_status=True):
        sent_email = cls.get_by_email_id(email_id)
        if sent_email:
            sent_email.block_status = block_status
            sent_email.put()                                        
    
    @classmethod
    def count_by_batch_id(cls, batch_id, limit=model_conf.MAX_FETCH_RECORD):
        return cls.query(ndb.AND(cls.batch_id==batch_id)).count(limit=limit)
    
    @classmethod
    def list_by_batch_id(cls, batch_id, offset=0, limit=model_conf.MAX_FETCH_RECORD):
        return cls.query(ndb.AND(cls.batch_id==batch_id)).fetch(offset=offset, limit=limit)
    
class Tagging(BaseNModel, DictModel):    
    label   = ndb.StringProperty(required=True)
    desc    = ndb.StringProperty(required=False)
    created_datetime    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    dict_properties = ['label', 'desc', 'created_datetime']
    
    @classmethod
    def create_tag(cls,parent=None, label=None, desc=None):
        created_tag = cls(
                            parent  = parent,
                            label   = label,
                            desc    = desc,
                            )
        
        created_tag.put()
        
        return created_tag
    
    @classmethod
    def get_by_label(cls, parent, label):
        return cls.query(ndb.AND(cls.label==label), ancestor=parent).fetch(limit=1)
    
        
        
    
    
    