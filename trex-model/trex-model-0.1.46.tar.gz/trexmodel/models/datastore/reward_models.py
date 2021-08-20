'''
Created on 22 Apr 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet, MerchantUser
from trexmodel.models.datastore.program_models import MerchantProgram
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexlib.utils.string_util import is_empty, is_not_empty
import logging
from trexmodel import conf, program_conf
from trexlib.utils.string_util import random_string
from datetime import datetime, timedelta
from trexmodel.utils.model.model_util import generate_transaction_id,\
    string_to_key_property

logger = logging.getLogger('model')


class RewardEntitlement(BaseNModel, DictModel):
    effective_date              = ndb.DateProperty(required=True)
    expiry_date                 = ndb.DateProperty(required=True)
    
    transaction_id              = ndb.StringProperty(required=True)
    
    invoice_id                  = ndb.StringProperty(required=False)
    
    rewarded_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    rewarded_by                 = ndb.KeyProperty(name="rewarded_by", kind=MerchantUser)
    rewarded_by_username        = ndb.StringProperty(required=False)
    
    reward_datetime_provided    = ndb.BooleanProperty(required=False, default=False)
    
    status                      = ndb.StringProperty(required=False, default=program_conf.REWARD_STATUS_VALID)
    
    reverted_datetime           = ndb.DateTimeProperty(required=False)
    reverted_by                 = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username        = ndb.StringProperty(required=False)
    
    @classmethod
    def list_by_transaction_id(cls, transaction_id):
        return cls.query(cls.transaction_id==transaction_id).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @property
    def is_valid(self):
        return self.status == program_conf.REWARD_STATUS_VALID
    
    @property
    def is_redeemed(self):
        return self.status == program_conf.REWARD_STATUS_REDEEMED
    
class CustomerEntitledReward(RewardEntitlement):
    '''
    Customer as ancestor
    '''
    
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    user_acct                   = ndb.KeyProperty(name="user_acct", kind=User)
    transact_outlet             = ndb.KeyProperty(name="transact_outlet", kind=Outlet)
    reward_program              = ndb.KeyProperty(name="reward_program", kind=MerchantProgram)
    
    @property
    def entitled_customer_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def rewarded_by_merchant_acct_entity(self):
        return MerchantAcct.fetch(self.merchant_acct.urlsafe())
    
    @property
    def reward_format(self):
        pass
    
    @property
    def reward_format_key(self):
        pass
    
    @property
    def reward_format_label(self):
        pass
    
    @property
    def rewarded_datetime_with_gmt(self):
        gmt_hour = self.rewarded_by_merchant_acct_entity.gmt_hour
        
        return self.rewarded_datetime + timedelta(hours=gmt_hour)
    
    @property
    def is_used(self):
        pass
    
    def revert(self, reverted_by, reverted_datetime=None):
        self.status = program_conf.REWARD_STATUS_REVERTED
        if reverted_datetime is None:
            reverted_datetime = datetime.now()
        
        self.reverted_datetime      = reverted_datetime
        self.reverted_by            = reverted_by.create_ndb_key()
        self.reverted_by_username   = reverted_by.username
        self.put()
    
    @classmethod
    def list_by_customer(cls, customer, status=program_conf.REWARD_STATUS_VALID, limit = conf.MAX_FETCH_RECORD):
        return cls.query(ndb.AND(cls.status==status), ancestor=customer.create_ndb_key()).fetch(limit=limit)

class CustomerCountableReward(CustomerEntitledReward):
    reward_amount               = ndb.FloatProperty(required=True, default=0)
    used_reward_amount          = ndb.FloatProperty(required=True, default=0)
    
    @property
    def reward_balance(self):
        return self.reward_amount - self.used_reward_amount
    
    def update_used_reward_amount(self, used_reward_amount, redeem_transaction_id):
        self.used_reward_amount += used_reward_amount
        reward_balance           = self.reward_balance
        
        logger.debug('CustomerCountableReward: reward_balance=%s', reward_balance)
        
        if reward_balance ==0:
            self.status = program_conf.REWARD_STATUS_REDEEMED
            self.redeem_transaction_id = redeem_transaction_id
        
        self.put()
    
    @classmethod
    def list_by_valid_with_cursor(cls, customer, limit=50, start_cursor=None):
        query = cls.query(ndb.AND(cls.status==program_conf.REWARD_STATUS_VALID
            ), ancestor=customer.create_ndb_key()).order(cls.expiry_date)
            
        (result, next_cursor) = cls.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
        
        return (result, next_cursor) 
    
    @property
    def is_used(self):
        return self.used_reward_amount>0
    
    @property
    def reward_brief(self):
        return 'Entitle {reward_amount} {reward_format}'.format(reward_amount=self.reward_amount, reward_format=self.reward_format_label)
    
    def to_reward_summary(self):
        return {
                'reward_format'         : self.reward_format, 
                'reward_amount'         : self.reward_amount,
                'used_reward_amount'    : self.used_reward_amount,
                'expiry_date'           : self.expiry_date.strftime('%d-%m-%Y'),
                }
    
    @classmethod
    def create(cls, reward_amount, customer_acct, transact_outlet,
               effective_date=None, expiry_date=None, 
               transaction_id=None, invoice_id=None,
               rewarded_by=None, program_key=None,
               rewarded_datetime = None
               ):
        
        if is_empty(transaction_id):
            transaction_id = generate_transaction_id()
            
        if effective_date is None:
            effective_date = datetime.today()
        
        if is_not_empty(program_key):
            reward_program          = string_to_key_property(program_key)
        
        customer_reward = cls(
                                            parent                  = customer_acct.create_ndb_key(),
                                            reward_amount           = reward_amount,
                                            transaction_id          = transaction_id,
                                            invoice_id              = invoice_id,
                                            
                                            merchant_acct           = customer_acct.merchant_acct,
                                            transact_outlet         = transact_outlet.create_ndb_key(),
                                            
                                            effective_date          = effective_date,
                                            expiry_date             = expiry_date,
                                            
                                            rewarded_by             = rewarded_by.create_ndb_key(),
                                            rewarded_by_username    = rewarded_by.username,
                                            
                                            reward_program          = reward_program,
                                            rewarded_datetime       = rewarded_datetime,
                                            
                                            )
        
        customer_reward.put()
        
        return customer_reward
    
class RevertedCustomerCountableReward(CustomerCountableReward):
    reverted_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    reverted_by                 = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username        = ndb.StringProperty(required=False)
    
    @classmethod
    def create(cls, customer_reward, reverted_by):
        reverted_customer_reward = cls(
                            parent                  = customer_reward.key.parent(),
                            reward_amount           = customer_reward.reward_amount,
                            transaction_id          = customer_reward.transaction_id,
                            invoice_id              = customer_reward.invoice_id,
                            
                            merchant_acct           = customer_reward.merchant_acct,
                            transact_outlet         = customer_reward.transact_outlet,
                            
                            effective_date          = customer_reward.effective_date,
                            expiry_date             = customer_reward.expiry_date,
                            
                            rewarded_by             = customer_reward.rewarded_by,
                            rewarded_by_username    = customer_reward.rewarded_by_username,
                            
                            reverted_by             = reverted_by.create_ndb_key(),
                            reverted_by_username    = reverted_by.username,
                            
                            )
        
        reverted_customer_reward.put()
        
class CustomerPointReward(CustomerCountableReward):
    
    @property
    def reward_format(self):
        return program_conf.REWARD_FORMAT_POINT
    
    @property
    def reward_format_label(self):
        return 'point(s)'

class CustomerStampReward(CustomerCountableReward):
    
    @property
    def reward_format(self):
        return program_conf.REWARD_FORMAT_STAMP
    
    @property
    def reward_format_label(self):
        return 'stamp(s)'
    

class RevertedCustomerPointReward(RevertedCustomerCountableReward):
    pass

class RevertedCustomerStampReward(RevertedCustomerCountableReward):
    pass
    
class CustomerEntitledVoucher(CustomerEntitledReward):
    
    entitled_voucher            = ndb.KeyProperty(name='entitled_voucher', kind=MerchantVoucher)
    
    redeem_code                 = ndb.StringProperty(required=False)
    redeemed_datetime           = ndb.DateTimeProperty(required=False)
    
    redeemed_by_outlet          = ndb.KeyProperty(name='redeemed_by_outlet', required=False)
    redeemed_by                 = ndb.KeyProperty(name="redeemed_by", kind=MerchantUser)
    redeemed_by_username        = ndb.StringProperty(required=False)
    
    redeemed_transaction_id     = ndb.StringProperty(required=False)
    
    removed_datetime            = ndb.DateTimeProperty(required=False)
    removed_by_username         = ndb.StringProperty(required=False)
    
    use_online                  = ndb.BooleanProperty(required=False, default=False)
    use_in_store                = ndb.BooleanProperty(required=False, default=False)
    
    dict_properties     = ['redeem_code', 'voucher_configuration', 'rewarded_by_username', 'rewarded_datetime', 'transaction_id', 
                           'invoice_id', 'merchant_reference_code', 'tags_list', 'status', 'is_reverted', 'is_used',
                           'registered_outlet_key', 'registered_merchant_acct_key', 'registered_datetime', 'modified_datetime']
    
    def redeem(self, redeemed_by, redeemed_datetime=None):
        self.status = program_conf.REWARD_STATUS_REDEEMED   
        
        if redeemed_datetime is None:
            redeemed_datetime = datetime.now()
        
        self.redeemed_datetime      = redeemed_datetime
        self.redeemed_by            = redeemed_by.create_ndb_key()
        self.redeemed_by_username   = redeemed_by.username
        self.put()
        
    @property
    def is_used(self):
        return self.status == program_conf.REWARD_STATUS_REDEEMED
    
    @property
    def is_reverted(self):
        return self.status == program_conf.REWARD_STATUS_REVERTED
    
    @property
    def transact_outlet_summary(self):
        return Outlet.fetch(self.transact_outlet.urlsafe())
    
    @property
    def voucher_configuration(self):
        voucher = MerchantVoucher.fetch(self.entitled_voucher.urlsafe())
        if voucher:
            return voucher.to_configuration()
    
    @property
    def entitled_voucher_key(self):
        return self.entitled_voucher.urlsafe().decode('utf-8')
    
    @property
    def entitled_voucher_entity(self):
        return MerchantVoucher.fetch(self.entitled_voucher.urlsafe())
    
    @staticmethod
    def create(entitled_voucher, customer_acct, transact_outlet, 
               effective_date=None, expiry_date=None,
               transaction_id=None, invoice_id=None,
               rewarded_by=None, rewarded_datetime=None):
        
        redeem_code = random_string(program_conf.REDEEM_CODE_LENGTH, is_human_mistake_safe=True)
        
        if is_empty(transaction_id):
            transaction_id = generate_transaction_id()
        
        customer_entiteld_voucher = CustomerEntitledVoucher(
                                            parent                  = customer_acct.create_ndb_key(),
                                            entitled_voucher        = entitled_voucher.create_ndb_key(),
                                            
                                            effective_date          = effective_date,
                                            expiry_date             = expiry_date,
                                            
                                            redeem_code             = redeem_code,
                                            transaction_id          = transaction_id,
                                            invoice_id              = invoice_id,
                                            
                                            merchant_acct           = customer_acct.merchant_acct,
                                            transact_outlet         = transact_outlet.create_ndb_key(),
                                            
                                            rewarded_by             = rewarded_by.create_ndb_key(),
                                            rewarded_by_username    = rewarded_by.username,
                                            
                                            rewarded_datetime       = rewarded_datetime,
                                            
                                            )
        
        customer_entiteld_voucher.put()
        
        return customer_entiteld_voucher
        
        
    @staticmethod
    def get_by_redeem_code(redeem_code):
        return  CustomerEntitledVoucher.query(CustomerEntitledVoucher.redeem_code==redeem_code).get()
    
    @staticmethod
    def list_by_customer(customer, limit=conf.MAX_FETCH_RECORD, offset=0, voucher_status=program_conf.REWARD_STATUS_VALID):
        return CustomerEntitledVoucher.query(ndb.AND(CustomerEntitledVoucher.status==voucher_status),
            ancestor=customer.create_ndb_key()).fetch(limit=limit, offset=offset)
    
    @staticmethod
    def update_customer_entiteld_voucher_summary(customer, voucher_status=program_conf.REWARD_STATUS_VALID):
        customers_vouchers_list = CustomerEntitledVoucher.list_by_customer(customer, voucher_status=voucher_status)
        entitled_voucher_summary   = {}
        if customers_vouchers_list:
            
            for customer_voucher in customers_vouchers_list:
                voucher         = customer_voucher.entitled_voucher
                voucher_key      = voucher.urlsafe().decode('utf-8')
                voucher_count    = entitled_voucher_summary.get(voucher_key)
                    
                if voucher_count:
                    entitled_voucher_summary[voucher_key] = voucher_count + 1
                else:
                    entitled_voucher_summary[voucher_key] = 1
        
        customer.entitled_voucher_summary = entitled_voucher_summary
        customer.put()
    
class VoucherRewardDetails(object):    
    
    def __init__(self, voucher_key, reward_amount, expiry_date, rewarded_datetime, merchant_acct=None):
        self.merchant_acct      = merchant_acct
        self.voucher_key        = voucher_key
        self.reward_amount      = reward_amount
        self.expiry_date        = expiry_date
        self.rewarded_datetime  = rewarded_datetime
        
    def __repr__(self, *args, **kwargs):
        return 'voucher_key=%s, reward_amount=%d, expiry_date=%s, rewarded_datetime=%s' % (self.voucher_key, self.reward_amount, self.expiry_date, self.rewarded_datetime)    
        
    @property
    def reward_format(self):
        return program_conf.REWARD_FORMAT_VOUCHER
    
    @property
    def reward_format_key(self):
        return self.voucher_key
    
    @property
    def rewarded_datetime_with_gmt(self):
        gmt_hour = self.merchant_acct.gmt_hour
        
        return self.rewarded_datetime + timedelta(hours=gmt_hour)
    