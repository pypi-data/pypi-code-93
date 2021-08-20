'''
Created on 1 Jun 2021

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet, MerchantUser
from trexlib.utils.string_util import is_empty, is_not_empty
import logging, json
from trexmodel import conf, program_conf
from datetime import datetime, timedelta
from trexmodel.utils.model.model_util import generate_transaction_id
from trexmodel.conf import SERVER_DATETIME_GMT
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.transaction_models import CustomerTransaction


logger = logging.getLogger('model')


class CustomerRedeemedItemUpstream(DictModel):
    
    dict_properties         = ['customer_key', 'merchant_key', 'redeemed_outlet_key', 'transaction_id', 'redeemed_amount',
                               'reward_format', 'voucher_key', 'redeemed_datetime', 'reverted',
                               'reverted_datetime', 'is_revert'
                               ]
    
    def __init__(self, customer_key=None, merchant_key=None, redeemed_outlet_key=None, transaction_id=None, redeemed_amount=0, reward_format=None, 
                 voucher_key=None, redeemed_datetime=None, reverted=False, reverted_datetime=None, is_revert=False):
        self.customer_key           = customer_key
        self.merchant_key           = merchant_key
        self.redeemed_outlet_key    = redeemed_outlet_key
        self.transaction_id         = transaction_id
        self.redeemed_amount        = redeemed_amount
        self.reward_format          = reward_format
        self.voucher_key            = voucher_key
        self.redeemed_datetime      = redeemed_datetime
        self.reverted               = reverted
        self.reverted_datetime      = reverted_datetime
        self.is_revert              = is_revert
        
        

class CustomerRedemption(BaseNModel, DictModel):
    '''
    Customer as ancestor
    '''
    
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    user_acct                   = ndb.KeyProperty(name="user_acct", kind=User)
    redeemed_outlet             = ndb.KeyProperty(name="redeemed_outlet", kind=Outlet)
    
    reward_format               = ndb.StringProperty(required=True)
    redeemed_amount             = ndb.FloatProperty(required=True, default=1)
    
    redeemed_summary            = ndb.JsonProperty(required=True)
    
    transaction_id              = ndb.StringProperty(required=True)
    invoice_id                  = ndb.StringProperty(required=False)
    remarks                     = ndb.StringProperty(required=False)
    
    status                      = ndb.StringProperty(required=True, default=program_conf.REDEEM_STATUS_VALID)
    
    redeemed_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    redeemed_by                 = ndb.KeyProperty(name="redeemed_by", kind=MerchantUser)
    redeemed_by_username        = ndb.StringProperty(required=False)
    
    reverted_datetime           = ndb.DateTimeProperty(required=False)
    reverted_by                 = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username        = ndb.StringProperty(required=False)
    
    dict_properties         = ['transaction_id', 'invoice_id', 'remarks', 'redeemed_amount', 'reward_format',
                               'redeemed_summary', 'redeemed_customer', 'redeemed_outlet_details', 'redeemed_merchant_acct',
                               'redeemed_datetime', 'is_revert',
                               'redeemed_by_username'
                               ]
    
    @staticmethod
    def list_by_transaction_id(cls, transaction_id):
        return cls.query(cls.transaction_id==transaction_id).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @property
    def is_valid(self):
        return self.status == program_conf.REDEEM_STATUS_VALID
    
    @property
    def is_revert(self):
        return self.status == program_conf.REDEEM_STATUS_REVERTED
    
    @property
    def redeemed_voucher_keys_list(self):
        return self.redeemed_summary.get('vouchers') 
    
    @property
    def redeemed_voucher_keys_list_in_str(self):
        vourchers =  self.redeemed_summary.get('vouchers')
        if vourchers:
            return json.dumps(vourchers)
        else:
            return ''
    
    @property
    def redeemed_merchant_acct(self):
        return MerchantAcct.fetch(self.merchant_acct.urlsafe())
    
    @property
    def redeemed_merchant_acct_key(self):
        return self.merchant_acct.urlsafe().decode('utf-8')
    
    @property
    def redeemed_outlet_key(self):
        return self.redeemed_outlet.urlsafe().decode('utf-8')
    
    @property
    def redeemed_outlet_details(self):
        return Outlet.fetch(self.redeemed_outlet_key)
    
    @property
    def redeemed_customer_key(self):
        return self.parent_key
    
    @property
    def redeemed_customer(self):
        return Customer.fetch(self.parent_key)
    
    @property
    def redeem_format_label(self):
        pass
    
    def revert(self, reverted_by, reverted_datetime=None):
        self.status = program_conf.REWARD_STATUS_REVERTED
        if reverted_datetime is None:
            reverted_datetime = datetime.now()
        
        self.reverted_datetime      = reverted_datetime
        self.reverted_by            = reverted_by.create_ndb_key()
        self.reverted_by_username   = reverted_by.username
        self.put()
    
    @staticmethod
    def list_by_customer(customer, status=program_conf.REWARD_STATUS_VALID, limit = conf.MAX_FETCH_RECORD):
        return CustomerRedemption.query(ndb.AND(CustomerRedemption.status==status), ancestor=customer.create_ndb_key()).fetch(limit=limit)
    
    @staticmethod
    def list_customer_redemption(customer_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = CustomerRedemption.query(ancestor = customer_acct.create_ndb_key()).order(-CustomerRedemption.redeemed_datetime)
        
        return CustomerRedemption.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_customer_redemption(customer_acct, limit=conf.MAX_FETCH_RECORD):
        query = CustomerRedemption.query(ancestor = customer_acct.create_ndb_key())
        
        return CustomerRedemption.count_with_condition_query(query, limit=limit)
    
    @staticmethod
    def create(customer, reward_format, redeemed_amount, redeemed_outlet, 
               redeemed_voucher_keys_list=None, invoice_id=None, remarks=None, redeemed_by=None, redeemed_datetime=None):
        
        reward_summary              = customer.reward_summary
        entitled_voucher_summary    = customer.entitled_voucher_summary
        
        if is_not_empty(redeemed_by):
            if isinstance(redeemed_by, MerchantUser):
                redeemed_by_username = redeemed_by.username

        
        redeem_transaction_id = generate_transaction_id(prefix='r')
        
        if redeemed_datetime is None:
            redeemed_datetime = datetime.now()
            redeemed_datetime = redeemed_datetime - timedelta(hours=int(SERVER_DATETIME_GMT))
        
        redeemed_summary = {}
        
        @model_transactional(desc='redeem reward')
        def __start_redeem(__customer, __total_redeemed_amount, cursor, reward_cls, reward_format):
            (result, next_cursor) = reward_cls.list_by_valid_with_cursor(__customer, limit=50, start_cursor=cursor)
            
            if result:
                redeemed_items_list = []
                for r in result:
                    reward_balance = r.reward_balance
                    
                    logger.debug('__start_redeem: reward_balance=%s',  reward_balance)
                    
                    if reward_balance<__total_redeemed_amount:
                        logger.debug('__start_redeem: redeem full amount from reward')
                        
                        __total_redeemed_amount -=reward_balance
                        r.update_used_reward_amount(reward_balance)
                        
                    else:
                        logger.debug('__start_redeem: redeem full amount from reward')
                        r.update_used_reward_amount(__total_redeemed_amount)
                        __total_redeemed_amount = 0
                        
                    logger.debug('__start_redeem: __total_redeemed_amount=%s',  __total_redeemed_amount)
                    
                    CustomerTransaction.update_transaction_reward_have_been_redeemed(r.transaction_id)
                    
                    redeemed_items_list.append({
                                                'key'               : r.key_in_str, 
                                                'redeemed_amount'   : reward_balance
                                                })
                    
                    if __total_redeemed_amount==0:
                        break
                
                return (__total_redeemed_amount, next_cursor,  redeemed_items_list)
            else:
                raise Exception('Reward not found')
        
        if reward_format == program_conf.REWARD_FORMAT_POINT:
            total_redeemed_amount   = redeemed_amount
            cursor                  = None
            redeemed_items_list     = [] 
            
            while total_redeemed_amount>0:
                (total_redeemed_amount, cursor, __redeemed_items_list) = __start_redeem(customer, total_redeemed_amount, cursor, 
                                                                                        CustomerPointReward)
                redeemed_items_list.extend(__redeemed_items_list)
            
            redeemed_summary = {
                                reward_format               : {
                                    
                                                                'amount'                    : redeemed_amount,        
                                                                'customer_point_rewards'    : redeemed_items_list
                                                                }
                                }
            
            reward_summary[reward_format]['amount'] -= redeemed_amount
                                
            
        elif reward_format == program_conf.REWARD_FORMAT_STAMP:
            total_redeemed_amount   = redeemed_amount
            cursor                  = None
            redeemed_items_list     = [] 
            
            while total_redeemed_amount>0:
                (total_redeemed_amount, cursor, __redeemed_items_list) = __start_redeem(customer, total_redeemed_amount, cursor, 
                                                                                        CustomerStampReward)
                redeemed_items_list.extend(__redeemed_items_list)
                
            redeemed_summary = {
                                reward_format               : {
                                    
                                                                'amount'                    : redeemed_amount,        
                                                                'customer_stamp_rewards'    : redeemed_items_list
                                                                }
                                
                                }
            
            reward_summary[reward_format]['amount'] -= redeemed_amount
            
        elif reward_format == program_conf.REWARD_FORMAT_VOUCHER:
            
            redemption_details = {
                                'vouchers': {}
                                }
            
            customer_entitled_voucher_list      = []
            voucher_redeem_codes_list           = []
            
            for v_k in redeemed_voucher_keys_list:
                customer_voucher        = CustomerEntitledVoucher.fetch(v_k)
                entitled_voucher_key    = customer_voucher.entitled_voucher_key
                redeemed_voucher_count  = redemption_details.get('vouchers').get(entitled_voucher_key)
                
                voucher_redeem_codes_list.append(customer_voucher.redeem_code)
                 
                if redeemed_voucher_count:
                    redemption_details.get('vouchers')[entitled_voucher_key] +=1
                else:
                    redemption_details.get('vouchers')[entitled_voucher_key] =1
                
                customer_voucher.redeem(redeemed_by, redeemed_datetime=redeemed_datetime)
                
                CustomerTransaction.update_transaction_reward_have_been_redeemed(customer_voucher.transaction_id)
                
                logger.debug('Voucher(%s) have been redeemed', customer_voucher.redeem_code)
                
                customer_entitled_voucher_list.append({
                                            'customer_entitled_voucher' : v_k
                                            })
                
            
            copied_entitled_voucher_summary = entitled_voucher_summary.copy()
            
            for v_k, v_info in  copied_entitled_voucher_summary.items():
                filtered_voucher_redeem_info_list = []
                
                for redeem_info in v_info.get('redeem_info_list'): 
                    if not redeem_info.get('redeem_code') in voucher_redeem_codes_list:
                        filtered_voucher_redeem_info_list.append(redeem_info)
                
                if filtered_voucher_redeem_info_list:
                    entitled_voucher_summary[v_k]['redeem_info_list'] = filtered_voucher_redeem_info_list
                else:
                    del entitled_voucher_summary[v_k]
            
            redemption_details['customer_entitled_vouchers'] = customer_entitled_voucher_list
            
            redeemed_summary = {
                                reward_format :   redemption_details
                                }
            
        customer_redemption = CustomerRedemption(
                                                    parent                  = customer.create_ndb_key(),
                                                    user_acct               = customer.registered_user_acct.create_ndb_key(),
                                                    merchant_acct           = customer.registered_merchant_acct.create_ndb_key(),
                                                    redeemed_outlet         = redeemed_outlet.create_ndb_key(),
                                                    reward_format           = reward_format,
                                                    redeemed_amount         = redeemed_amount,
                                                    redeemed_summary        = redeemed_summary,
                                                    
                                                    transaction_id          = redeem_transaction_id,
                                                    invoice_id              = invoice_id,
                                                    remarks                 = remarks,
                                                    
                                                    redeemed_by             = redeemed_by.create_ndb_key(),
                                                    redeemed_by_username    = redeemed_by_username,
                                                    
                                                    redeemed_datetime       = redeemed_datetime,
                                                    
                                                    )
        
        
        customer_redemption.put()
        
        customer.reward_summary             = reward_summary
        customer.entitled_voucher_summary   = entitled_voucher_summary
        customer.put()
        
        return customer_redemption
    
    @staticmethod
    def list_redemption_by_date(redeemed_date, redeemed_outlet=None, including_reverted_transaction=True, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        
        redeemed_datetime           = datetime.combine(redeemed_date, datetime.min.time())
        next_day_redeemed_datetimee = redeemed_datetime + timedelta(days=1)
        
        logger.debug('redeemed_datetime=%s',redeemed_datetime)
        logger.debug('next_day_redeemed_datetimee=%s',next_day_redeemed_datetimee)
        
        if redeemed_outlet:
            if including_reverted_transaction:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    CustomerRedemption.redeemed_outlet == redeemed_outlet.create_ndb_key(),
                                    )).order(-CustomerRedemption.redeemed_datetime)
            else:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    CustomerRedemption.redeemed_outlet == redeemed_outlet.create_ndb_key(),
                                    CustomerRedemption.status == program_conf.REDEEM_STATUS_VALID,
                                    )).order(-CustomerRedemption.redeemed_datetime)
        else:
            if including_reverted_transaction:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    )).order(-CustomerRedemption.redeemed_datetime)
            else:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    CustomerRedemption.status == program_conf.REDEEM_STATUS_VALID,
                                    )).order(-CustomerRedemption.redeemed_datetime)
        
        return CustomerRedemption.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_redemption_by_date(transact_date, including_reverted_transaction=True, redeemed_outlet=None, limit=conf.MAX_FETCH_RECORD):
        
        redeemed_datetime           = datetime.combine(transact_date, datetime.min.time())
        next_day_redeemed_datetimee = redeemed_datetime + timedelta(days=1)
        
        logger.debug('redeemed_datetime=%s',redeemed_datetime)
        logger.debug('next_day_transact_datetime=%s',next_day_redeemed_datetimee)
        
        if redeemed_outlet:
            if including_reverted_transaction:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    CustomerRedemption.redeemed_outlet == redeemed_outlet.create_ndb_key()
                                    ))
            else:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    CustomerRedemption.redeemed_outlet == redeemed_outlet.create_ndb_key(),
                                    CustomerRedemption.status == program_conf.REDEEM_STATUS_VALID,
                                    ))
        else:
            if including_reverted_transaction:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    ))
            else:
                query = CustomerRedemption.query(ndb.AND(
                                    CustomerRedemption.redeemed_datetime  >= redeemed_datetime,
                                    CustomerRedemption.redeemed_datetime  <  next_day_redeemed_datetimee,
                                    CustomerRedemption.status != program_conf.REDEEM_STATUS_REVERTED,
                                    ))
        
        return CustomerRedemption.count_with_condition_query(query, limit=limit)
    
class RedemptionItemDetails(BaseNModel):
    transaction_id              = ndb.StringProperty(required=True)
        
    
    