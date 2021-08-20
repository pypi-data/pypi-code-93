'''
Created on 10 Mar 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct, \
    MerchantUser
import logging
from trexmodel import program_conf
from datetime import datetime

logger = logging.getLogger('model')

class VoucherBase(BaseNModel, DictModel):
    label                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=False)
    terms_and_conditions    = ndb.TextProperty(required=False)
    completed_status        = ndb.StringProperty(required=True, choices=set(program_conf.VOUCHER_STATUS))
    configuration           = ndb.JsonProperty(required=False, default={})
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    published_datetime      = ndb.DateTimeProperty(required=False)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username    = ndb.StringProperty(required=False)
    
    published               = ndb.BooleanProperty(default=False)
    archived                = ndb.BooleanProperty(default=False)
    image_storage_filename  = ndb.StringProperty(required=False)
    image_public_url        = ndb.StringProperty(required=False)
    
    dict_properties         = ['label', 'desc', 'terms_and_conditions', 'configuration', 'created_datetime', 'modified_datetime', 'completed_status', 
                               'created_by_username', 'modified_by_username', 'is_published', 'is_archived',  
                               'image_public_url','image_storage_filename']
    
    @property
    def is_archived(self):
        return self.archived
    
    @property
    def is_published(self):
        return self.completed_status == program_conf.VOUCHER_STATUS_PUBLISH
    
class MerchantVoucher(VoucherBase):
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    def to_voucher_configuration(self):
        voucher_configuration = {
                                'voucher_key'           : self.key_in_str,
                                'voucher_configuration' : self.configuration,
                                'terms_and_conditions'  : self.terms_and_conditions,
                                'image_public_url'      : self.image_public_url,
                                }
        
        return voucher_configuration
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None, terms_and_conditions=None, voucher_image_url=None, created_by=None):
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        
        merchant_voucher =  MerchantVoucher(
                                        parent                  = merchant_acct.create_ndb_key(),
                                        label                   = label,
                                        desc                    = desc,
                                        terms_and_conditions    = terms_and_conditions,
                                        created_by              = created_by.create_ndb_key(),
                                        created_by_username     = created_by_username,
                                        configuration           = {},
                                        completed_status        = program_conf.VOUCHER_STATUS_BASE,
                                        image_public_url        = voucher_image_url,
                                        )
        
        merchant_voucher.put()
        return merchant_voucher
    
    @staticmethod
    def update_voucher_base_data(merchant_voucher, label=None, desc=None, terms_and_conditions=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.label                  = label
        merchant_voucher.desc                   = desc
        merchant_voucher.terms_and_conditions   = terms_and_conditions
        merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_BASE
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def update_voucher_configuration_data(merchant_voucher, configuration=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.configuration          = configuration
        merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_CONFIGURATION
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def update_voucher_material(merchant_voucher, image_public_url=None, image_storage_filename=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.image_public_url       = image_public_url
        merchant_voucher.image_storage_filename = image_storage_filename
        
        if merchant_voucher.completed_status!=program_conf.VOUCHER_STATUS_PUBLISH:
            merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_UPLOAD_MATERIAL 
        
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def update_voucher_material_uploaded(merchant_voucher, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_UPLOAD_MATERIAL
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def publish_voucher(voucher):
        voucher.completed_status    = program_conf.VOUCHER_STATUS_PUBLISH
        voucher.apublished_datetime = datetime.now()
        voucher.put()
        
        merchant_acct = voucher.merchant_acct
        merchant_acct.update_published_voucher(voucher.to_voucher_configuration())    
        
    @staticmethod
    def archive_voucher(voucher):
        voucher.archived = True
        voucher.archived_datetime = datetime.now()
        voucher.put()
        
        merchant_acct = voucher.merchant_acct
        merchant_acct.remove_archieve_voucher(voucher.key_in_str)    
    
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        return MerchantVoucher.query(ndb.AND(MerchantVoucher.archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_archived_by_merchant_account(merchant_acct):
        return MerchantVoucher.query(ndb.AND(MerchantVoucher.archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_published_by_merchant_account(merchant_acct):
        return MerchantVoucher.query(ndb.AND(MerchantVoucher.completed_status==program_conf.VOUCHER_STATUS_PUBLISH), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)

class BrandVouhcer(VoucherBase):
    #merchant_acct           = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    pass
