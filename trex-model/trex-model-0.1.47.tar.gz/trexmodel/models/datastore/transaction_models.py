'''
Created on 1 Apr 2021

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.customer_models import Customer
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet,\
    MerchantUser
import logging
from trexmodel import conf, program_conf
from datetime import datetime,date, timedelta
from trexmodel.conf import SERVER_DATETIME_GMT
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher
from trexmodel.models.datastore.customer_model_helpers import update_reward_summary_with_reverted_reward,\
    update_customer_entiteld_voucher_summary_after_reverted
from trexmodel.utils.model.model_util import generate_transaction_id
from gettext import gettext

logger = logging.getLogger('model')


class CustomerTransaction(BaseNModel, DictModel):
    '''
    
    '''
    transact_merchant           = ndb.KeyProperty(name="transact_merchant", kind=MerchantAcct)
    transact_outlet             = ndb.KeyProperty(name="transact_outlet", kind=Outlet)
    
    transact_datetime           = ndb.DateTimeProperty(required=True)
    created_datetime            = ndb.DateTimeProperty(required=True, auto_now=True)
    
    transaction_id              = ndb.StringProperty(required=True)
    invoice_id                  = ndb.StringProperty(required=False)
    remarks                     = ndb.StringProperty(required=False)
    
    tax_amount                  = ndb.FloatProperty(required=False, default=.0)
    transact_amount             = ndb.FloatProperty(required=True)
    
    transact_by                 = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    transact_by_username        = ndb.StringProperty(required=False)
    
    entitled_reward_summary     = ndb.JsonProperty()
    entitled_voucher_summary    = ndb.JsonProperty()
    
    reward_giveaway_method      = ndb.StringProperty(required=False, default=program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM)
    
    is_revert                   = ndb.BooleanProperty(required=False, default=False)
    reverted_datetime           = ndb.DateTimeProperty(required=False)
    reverted_by                 = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username        = ndb.StringProperty(required=False)
    
    is_reward_redeemed          = ndb.BooleanProperty(required=False, default=False)
    
    dict_properties         = ['transaction_id', 'invoice_id', 'remarks', 'tax_amount', 'transact_amount', 'reward_giveaway_method',
                               'entitled_reward_summary', 'entitled_voucher_summary', 'transact_customer_acct', 'transact_outlet_details', 'transact_merchant_acct',
                               'transact_datetime', 'created_datetime',  'transact_outlet_key', 'is_revert', 'reverted_datetime',
                               'transact_by_username'
                               ]
    
    def to_transaction_details_json(self):
        pass
    
    @property
    def transact_customer_acct(self):
        return Customer.fetch(self.key.parent().urlsafe())
    
    @property
    def transact_user_acct_key(self):
        return Customer.fetch(self.key.parent().urlsafe()).registered_user_acct_key
    
    @property
    def transact_merchant_acct(self):
        return MerchantAcct.fetch(self.transact_merchant.urlsafe())
    
    @property
    def transact_outlet_key(self):
        return self.transact_outlet.urlsafe()
    
    @property
    def transact_merchant_acct_key(self):
        return self.transact_merchant.urlsafe()
    
    @property
    def transact_customer_key(self):
        return self.key.parent().urlsafe()
    
    @property
    def transact_outlet_details(self):
        return Outlet.fetch(self.transact_outlet.urlsafe())
    
    @property
    def transact_by_user(self):
        return MerchantUser.fetch(self.transact_by.urlsafe())
    
    @staticmethod
    def update_transaction_reward_have_been_redeemed(transaction_id):
        
        logger.debug('Update customer transaction reward have been redeemed by transaction id=%s', transaction_id)
        
        if transaction_id:
            customer_transaction = CustomerTransaction.get_by_transaction_id(transaction_id)
            if customer_transaction:
                customer_transaction.is_reward_redeemed = True
                customer_transaction.put()
    
    @staticmethod
    def create_manual_transaction(customer, remarks=None, transact_outlet=None, transact_by=None, transact_datetime=None): 
        return CustomerTransaction.create_system_transaction(customer, remarks=remarks, transact_outlet=transact_outlet, transact_by=transact_by, 
                                   transact_datetime=transact_datetime, reward_giveaway_method=program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_MANUAL,
                                   )
    
    @staticmethod
    def create_system_transaction(customer, transact_amount=.0, tax_amount=.0, invoice_id=None, remarks=None, 
               transact_outlet=None, transact_by=None, transact_datetime=None, reward_giveaway_method=program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM,
               ):
        
        if is_not_empty(transact_by):
            if isinstance(transact_by, MerchantUser):
                transact_by_username = transact_by.username

        
        transaction_id = generate_transaction_id()
        
        if transact_datetime is None:
            transact_datetime = datetime.now()
            transact_datetime = transact_datetime - timedelta(hours=int(SERVER_DATETIME_GMT))
        
        logger.debug('generated transaction_id=%s', transaction_id)
        logger.debug('invoice_id=%s', invoice_id)
        logger.debug('tax_amount=%s', tax_amount)
        logger.debug('transact_amount=%s', transact_amount)
        logger.debug('transact_datetime=%s', transact_datetime)
        logger.debug('transact_by_username=%s', transact_by_username)
        
        customer_transaction = CustomerTransaction(
                                                    parent                  = customer.create_ndb_key(),
                                                    
                                                    transact_merchant       = customer.registered_merchant_acct.create_ndb_key(),
                                                    transact_outlet         = transact_outlet.create_ndb_key(),
                                                    
                                                    tax_amount              = tax_amount,
                                                    transact_amount         = transact_amount,
                                                    
                                                    transaction_id          = transaction_id,
                                                    invoice_id              = invoice_id,
                                                    remarks                 = remarks,
                                                    
                                                    transact_by             = transact_by.create_ndb_key(),
                                                    transact_by_username    = transact_by_username,
                                                    
                                                    transact_datetime       = transact_datetime,
                                                    reward_giveaway_method  = reward_giveaway_method,
                                                    )
        
        customer_transaction.put()
        customer.put()
        
        return customer_transaction
    
    def revert(self, customer_acct, reverted_by):
        transaction_id = self.transaction_id
        
        entitled_point_details_list     = CustomerPointReward.list_by_transaction_id(transaction_id)
        
        entitled_stamp_details_list     = CustomerStampReward.list_by_transaction_id(transaction_id)
        
        entiteld_vouchers_list          = CustomerEntitledVoucher.list_by_transaction_id(transaction_id)
        
        is_transaction_reward_used      = False
        
        customer_reward_summary     = customer_acct.reward_summary or {}
        entitled_voucher_summary    = customer_acct.entitled_voucher_summary or {}
        
        logger.debug('revert: transaction_id=%s', transaction_id)
        logger.debug('revert: entitled_point_details_list count=%s', len(entitled_point_details_list))
        logger.debug('revert: entitled_stamp_details_list count=%s', len(entitled_stamp_details_list))
        logger.debug('revert: entiteld_vouchers_list count=%s', len(entiteld_vouchers_list))
        
        for p in entitled_point_details_list:
            if p.is_used:
                is_transaction_reward_used = True
                break
        
        if is_transaction_reward_used is False:
            for p in entitled_stamp_details_list:
                if p.is_used:
                    is_transaction_reward_used = True
                    break
                
        if is_transaction_reward_used is False:
            for p in entiteld_vouchers_list:
                if p.is_used:
                    is_transaction_reward_used = True
                    break
        
        logger.debug('revert: is_transaction_reward_used=%s', is_transaction_reward_used)
        
        if is_transaction_reward_used is False:
            
            logger.debug('Going to revert transqction')
            reverted_by_key                 = reverted_by.create_ndb_key()
            
            reverted_datetime               = datetime.now()
            self.is_revert                  = True
            self.reverted_datetime          = reverted_datetime
            self.reverted_by                = reverted_by_key
            self.reverted_by_username       = reverted_by.username
            self.put()
            
            for p in entitled_point_details_list:
                if p.is_valid:
                    customer_reward_summary = update_reward_summary_with_reverted_reward(customer_reward_summary, p.to_reward_summary())
                    p.status                        = program_conf.REWARD_STATUS_REVERTED
                    p.reverted_datetime             = reverted_datetime
                    p.reverted_by                   = reverted_by_key
                    p.reverted_by_username          = reverted_by.username
                    p.put()
                    
                
            for p in entitled_stamp_details_list:
                if p.is_valid:
                    customer_reward_summary = update_reward_summary_with_reverted_reward(customer_reward_summary, p.to_reward_summary())
                    p.status                        = program_conf.REWARD_STATUS_REVERTED
                    p.reverted_datetime             = reverted_datetime
                    p.reverted_by                   = reverted_by_key
                    p.reverted_by_username          = reverted_by.username
                    p.put()
                
            for p in entiteld_vouchers_list:
                if p.is_valid:
                    p.status                        = program_conf.REWARD_STATUS_REVERTED
                    p.reverted_datetime             = reverted_datetime
                    p.reverted_by                   = reverted_by_key
                    p.reverted_by_username          = reverted_by.username
                    p.put()
                    
                    entitled_voucher_summary = update_customer_entiteld_voucher_summary_after_reverted(entitled_voucher_summary, p)
            
            updated_voucher_summary = {}
            
            for voucher_key, count in entitled_voucher_summary.items():
                if count>0:
                    updated_voucher_summary[voucher_key] = count
                
            customer_acct.reward_summary            = customer_reward_summary
            customer_acct.entitled_voucher_summary  = updated_voucher_summary or {}
            customer_acct.put()
            
            return True
        
        else:
            raise Exception(gettext('Transaction reward have been used'))
    
    @staticmethod
    def list_customer_transaction(customer_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = CustomerTransaction.query(ancestor = customer_acct.create_ndb_key()).order(-CustomerTransaction.transact_datetime)
        
        return CustomerTransaction.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def get_by_transaction_id(transaction_id):
        return CustomerTransaction.query(CustomerTransaction.transaction_id==transaction_id).get()
    
    @staticmethod
    def get_by_invoice_id(invoice_id):
        return CustomerTransaction.query(CustomerTransaction.invoice_id==invoice_id).get()
    
    @staticmethod
    def list_transaction_by_date(transact_date, transact_outlet=None, including_reverted_transaction=True, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        
        transact_datetime           = datetime.combine(transact_date, datetime.min.time())
        next_day_transact_datetime  = transact_datetime + timedelta(days=1)
        
        logger.debug('transact_datetime=%s',transact_datetime)
        logger.debug('next_day_transact_datetime=%s',next_day_transact_datetime)
        
        if transact_outlet:
            if including_reverted_transaction:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    CustomerTransaction.transact_outlet == transact_outlet.create_ndb_key(),
                                    )).order(-CustomerTransaction.transact_datetime)
            else:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    CustomerTransaction.transact_outlet == transact_outlet.create_ndb_key(),
                                    CustomerTransaction.is_revert == False,
                                    )).order(-CustomerTransaction.transact_datetime)
        else:
            if including_reverted_transaction:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    )).order(-CustomerTransaction.transact_datetime)
            else:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    CustomerTransaction.is_revert == False,
                                    )).order(-CustomerTransaction.transact_datetime)
        
        return CustomerTransaction.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def list_all(offset=0, limit=conf.MAX_FETCH_RECORD):
        
        query = CustomerTransaction.query()
        
        return CustomerTransaction.list_all_with_condition_query(query, offset=offset, limit=limit)
    
    @staticmethod
    def count_customer_transaction(customer_acct, limit=conf.MAX_FETCH_RECORD):
        query = CustomerTransaction.query(ancestor = customer_acct.create_ndb_key())
        
        return CustomerTransaction.count_with_condition_query(query, limit=limit)
    
    @staticmethod
    def count_transaction_by_date(transact_date, including_reverted_transaction=True, transact_outlet=None, limit=conf.MAX_FETCH_RECORD):
        
        transact_datetime           = datetime.combine(transact_date, datetime.min.time())
        next_day_transact_datetime  = transact_datetime + timedelta(days=1)
        
        logger.debug('transact_datetime=%s',transact_datetime)
        logger.debug('next_day_transact_datetime=%s',next_day_transact_datetime)
        
        if transact_outlet:
            if including_reverted_transaction:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    CustomerTransaction.transact_outlet == transact_outlet.create_ndb_key()
                                    ))
            else:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    CustomerTransaction.transact_outlet == transact_outlet.create_ndb_key(),
                                    CustomerTransaction.is_revert == False,
                                    ))
        else:
            if including_reverted_transaction:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    ))
            else:
                query = CustomerTransaction.query(ndb.AND(
                                    CustomerTransaction.transact_datetime  >= transact_datetime,
                                    CustomerTransaction.transact_datetime  <  next_day_transact_datetime,
                                    CustomerTransaction.is_revert == False,
                                    ))
        
        return CustomerTransaction.count_with_condition_query(query, limit=limit)
    
class CustomerTransactionWithRewardDetails(object):    
    
    def __init__(self, transaction_details, reward_details):
        self.transact_customer_key          = transaction_details.transact_customer_key
        self.transact_merchant_acct_key     = transaction_details.transact_merchant_acct_key
        self.transact_outlet_key            = transaction_details.transact_outlet_key
        self.transact_datetime              = transaction_details.transact_datetime
        self.transaction_id                 = transaction_details.transaction_id
        self.transact_amount                = transaction_details.transact_amount
        self.is_revert                      = transaction_details.is_revert
        self.reverted_datetime              = transaction_details.reverted_datetime
        self.reward_format                  = reward_details.reward_format
        self.reward_amount                  = reward_details.reward_amount
        self.expiry_date                    = reward_details.expiry_date
        self.rewarded_datetime              = reward_details.rewarded_datetime 
        self.reward_format_key              = reward_details.reward_format_key
        
    
    
    
    
        
      
        
        
    
        