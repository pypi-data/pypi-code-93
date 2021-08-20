'''
Created on 7 Apr 2021

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct, \
    MerchantUser
import logging

from datetime import datetime

logger = logging.getLogger('model')

class MembershipBase(BaseNModel, DictModel):
    '''
    Merchant Acct as ancestor
    
    '''
    
    label                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=False)
    
    expiration_type         = ndb.StringProperty(required=True)
    expiration_value        = ndb.IntegerProperty(required=False)
    
    archived                = ndb.BooleanProperty(default=False)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username    = ndb.StringProperty(required=False)

    dict_properties         = ['label', 'desc', 'expiration_type', 'expiration_value', 'created_datetime', 'modified_datetime']
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @classmethod
    def list_by_merchant_acct(cls, merchant_acct, is_archived=False):
        return cls.query(ndb.AND(MerchantMembership.archived == is_archived), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @classmethod
    def create(cls, merchant_acct, label, desc=None, expiration_type=None, expiration_value=None, 
               created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        merchant_membership = cls(
                                                parent                  = merchant_acct.create_ndb_key(),
                                                label                   = label,
                                                desc                    = desc,
                                                expiration_type         = expiration_type,
                                                expiration_value        = expiration_value,
                                                created_by              = created_by.create_ndb_key(),
                                                created_by_username     = created_by_username,
                                                )
        
        merchant_membership.put()
        
        return merchant_membership
    
    @classmethod
    def update(cls, merchant_membership, label, desc=None, expiration_type=None, expiration_value=None, 
               modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_membership.label                   = label
        merchant_membership.desc                    = desc
        merchant_membership.expiration_type         = expiration_type
        merchant_membership.expiration_value        = expiration_value
        merchant_membership.modified_by             = modified_by.create_ndb_key()
        merchant_membership.modified_by_username    = modified_by_username
        
        merchant_membership.put()

class MerchantMembership(MembershipBase):
    
    
    def to_configuration(self):
        membership_configuration = {
                                    'membership_key'                : self.key_in_str,
                                    'label'                         : self.label,
                                    'expiration_type'               : self.expiration_type,
                                    'expiration_value'              : self.expiration_value,
                                    }
        
        return membership_configuration
    
    @staticmethod
    def archive_membership(membership):
        membership.archived = True
        membership.archived_datetime = datetime.now()
        membership.put()
        
        merchant_acct = membership.merchant_acct
        merchant_acct.remove_archieve_basic_membership(membership.key_in_str)    
        
    


class MerchantTierMembership(MembershipBase):        
    entitle_qualification_type          = ndb.StringProperty(required=True)
    entitle_qualification_value         = ndb.FloatProperty(required=False)
    upgrade_expiry_type                 = ndb.StringProperty(required=True)
    
    dict_properties         = ['label', 'desc', 'expiration_type', 'expiration_value', 'entitle_qualification_type', 
                               'entitle_qualification_value', 'upgrade_expiry_type', 'created_datetime', 'modified_datetime'
                               ]
    
    
    def to_configuration(self):
        membership_configuration = {
                                    'membership_key'                : self.key_in_str,
                                    'label'                         : self.label,
                                    'expiration_type'               : self.expiration_type,
                                    'expiration_value'              : self.expiration_value,
                                    'entitle_qualification_type'    : self.entitle_qualification_type,
                                    'entitle_qualification_value'   : self.entitle_qualification_value,
                                    'upgrade_expiry_type'           : self.upgrade_expiry_type,
                                    }
        
        return membership_configuration
        
    @staticmethod
    def create(merchant_acct, label=None, desc=None, expiration_type=None, expiration_value=None, 
               entitle_qualification_type=None, entitle_qualification_value=None, upgrade_expiry_type=None,
               created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        merchant_membership = MerchantTierMembership(
                                                parent                          = merchant_acct.create_ndb_key(),
                                                label                           = label,
                                                desc                            = desc,
                                                expiration_type                 = expiration_type,
                                                expiration_value                = expiration_value,
                                                entitle_qualification_type      = entitle_qualification_type,
                                                entitle_qualification_value     = entitle_qualification_value,
                                                upgrade_expiry_type             = upgrade_expiry_type,
                                                created_by                      = created_by.create_ndb_key(),
                                                created_by_username             = created_by_username,
                                                )
        
        merchant_membership.put()
        
        membership_key = merchant_membership.key_in_str
        
        logger.debug('membership_key=%s', membership_key)
        
        merchant_acct.add_tier_membership(merchant_membership.to_configuration())
        
        return merchant_membership
    
    @staticmethod
    def update(merchant_membership, label=None, desc=None, expiration_type=None, expiration_value=None, 
               entitle_qualification_type=None, entitle_qualification_value=None, upgrade_expiry_type=None,
               modified_by=None):
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_membership.label                           = label
        merchant_membership.desc                            = desc
        merchant_membership.expiration_type                 = expiration_type
        merchant_membership.expiration_value                = expiration_value
        merchant_membership.entitle_qualification_type      = entitle_qualification_type
        merchant_membership.entitle_qualification_value     = entitle_qualification_value
        merchant_membership.entitle_qualification_value     = entitle_qualification_value
        merchant_membership.upgrade_expiry_type             = upgrade_expiry_type
        merchant_membership.modified_by_username            = modified_by_username
        
        merchant_membership.put()
        
        merchant_acct = merchant_membership.merchant_acct
        
        merchant_acct.update_tier_membership(merchant_membership.to_configuration())
        
        return merchant_membership
    
    @staticmethod
    def archive_membership(membership):
        membership.archived = True
        membership.archived_datetime = datetime.now()
        membership.put()
        
        merchant_acct = membership.merchant_acct
        merchant_acct.remove_archieve_tier_membership(membership.key_in_str)   
            