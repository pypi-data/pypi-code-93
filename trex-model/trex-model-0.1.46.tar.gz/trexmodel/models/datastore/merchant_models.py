'''
Created on 15 May 2020

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
from trexmodel.models.datastore.system_models import SentEmail
from trexmodel.models.datastore.user_models import UserMin
import trexmodel.conf as model_conf
from trexlib.utils.security_util import generate_user_id, hash_password
from trexlib.utils.string_util import random_number, is_empty, is_not_empty,\
    split_by_length, random_string
import logging, hashlib
from datetime import datetime, timedelta
from trexlib.utils.common.date_util import parse_datetime
from trexmodel import conf, program_conf
from google.auth._default import default
from trexmodel.models.datastore.system_models import Tagging

logger = logging.getLogger('model')

class MerchantMin(BaseNModel, DictModel, FullTextSearchable):
    
    company_name                = ndb.StringProperty(required=True)
    contact_name                = ndb.StringProperty(required=False)
    address                     = ndb.StringProperty(required=False)
    office_phone                = ndb.StringProperty(required=False)
    mobile_phone                = ndb.StringProperty(required=False)
    fax_phone                   = ndb.StringProperty(required=False)
    email                       = ndb.StringProperty(required=False)
    country                     = ndb.StringProperty(required=False, default='my')
    status                      = ndb.StringProperty(required=False)
    
    modified_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)
    registered_datetime         = ndb.DateTimeProperty(required=True, auto_now_add=True)
    plan_start_date             = ndb.DateProperty(required=True)
    plan_end_date               = ndb.DateProperty(required=True)
    
    fulltextsearch_field_name   = 'company_name'
    
    
    @property
    def gmt_hour(self):
        return conf.DEFAULT_GMT_HOURS
    

class MerchantAcct(MerchantMin):
    account_code                            = ndb.StringProperty(required=False)
    logo_public_url                         = ndb.StringProperty(required=False)
    logo_storage_filename                   = ndb.StringProperty(required=False)
    dashboard_stat_figure                   = ndb.JsonProperty()
    currency_code                           = ndb.StringProperty(required=False, default='myr')
    api_key                                 = ndb.StringProperty(required=False)
    
    
    published_program_configuration         = ndb.JsonProperty()
    published_voucher_configuration         = ndb.JsonProperty()
    membership_configuration                = ndb.JsonProperty()
    tier_membership_configuration           = ndb.JsonProperty()
    
    stat_figure_update_interval_in_minutes  = conf.MERCHANT_STAT_FIGURE_UPDATE_INTERVAL_IN_MINUTES
    stat_figure_update_datetime_format      = '%d-%m-%Y %H:%M:%S'
    
    dict_properties = ['company_name', 'contact_name', 'mobile_phone', 'office_phone', 'fax_phone', 'email', 'account_code', 'country',
                       'registered_datetime', 'modified_datetime', 'plan_start_date', 'plan_end_date', 'currency_code', 
                       'published_program_configuration', 'published_voucher_configuration', 'membership_configuration', 
                       'tier_membership_configuration']
    
    @staticmethod
    def format_account_code(account_code):
        if is_not_empty(account_code):
            if len(account_code) == 16:
                account_code = '-'.join(split_by_length(account_code,4))
        return account_code    
    
    @staticmethod
    def search_merchant_account(company_name=None, account_code=None,
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list = None
        query = MerchantAcct.query()
        
        if is_not_empty(company_name):
            search_text_list = company_name.split(' ')
            
        elif is_not_empty(account_code):
            query = query.filter(MerchantAcct.account_code==account_code)
            
        
        
        total_count                         = MerchantAcct.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = MerchantAcct.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
    
    @property
    def manual_giveaway_reward_program_list(self):
        published_program_configuration = self.published_program_configuration
        program_list = []
        
        for program in published_program_configuration.get('programs'):
            if program.get('reward_base') == program_conf.REWARD_BASE_ON_GIVEAWAY:
                if program.get('giveaway_method') == program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_MANUAL:
                    program_list.append(program)
        
        
        return program_list
    
    def update_api_key(self):
        api_key = random_string(24)
        logger.debug('api_key=%s', api_key)
        self.api_key = api_key
        self.put()
        
        return api_key
    
    def flush_dirty_program_configuration(self):
        if self.published_program_configuration and len(self.published_program_configuration)>0:
            existing_programs_list  = self.published_program_configuration.get('programs')
            new_programs_list       = []
            for p in existing_programs_list:
                try:
                    program = ndb.Key(urlsafe=p.get('program_key')).get()
                    if program.archived is False:
                        new_programs_list.append(p)
                except:
                    pass
            
            self.published_program_configuration['programs']    = new_programs_list
            self.published_program_configuration['count']       = len(new_programs_list)
        else:
            self.published_program_configuration = {'programs':[], 'count':0}
            
        self.put()
        
    
    def flush_dirty_membership_configuration(self):    
        if self.membership_configuration and len(self.membership_configuration.get('memberships'))>0:
            existing_memberships_list  = self.membership_configuration.get('memberships')
            new_memberships_list       = []
            for p in existing_memberships_list:
                try:
                    membership = ndb.Key(urlsafe=p.get('membership_key')).get()
                    if membership.archived is False:
                        new_memberships_list.append(p)
                except:
                    pass
            
            self.membership_configuration['memberships'] = new_memberships_list
            self.membership_configuration['count']       = len(new_memberships_list)
            
        else:
            self.membership_configuration = {'memberships':[], 'count':0}
        
        self.put()
        
    def flush_dirty_tier_membership_configuration(self):    
        if self.tier_membership_configuration and len(self.tier_membership_configuration.get('memberships'))>0:
            existing_memberships_list  = self.tier_membership_configuration.get('memberships')
            new_memberships_list       = []
            for p in existing_memberships_list:
                try:
                    membership = ndb.Key(urlsafe=p.get('membership_key')).get()
                    if membership.archived is False:
                        new_memberships_list.append(p)
                except:
                    pass
            
            self.tier_membership_configuration['memberships'] = new_memberships_list
            self.tier_membership_configuration['count']       = len(new_memberships_list)
            
        else:
            self.tier_membership_configuration = {'memberships':[], 'count':0}
        
        self.put()
        
    def flush_and_update_membership_configuration(self, memberships_list):    
        
        logger.debug('flush_and_update_membership_configuration: memberships_list count=%d ', len(memberships_list))
        
        membership_configuration_list = []
        
        for m in memberships_list:
            membership_configuration_list.append(m.to_configuration())
            
        self.membership_configuration = {'memberships':membership_configuration_list, 'count':len(membership_configuration_list)}
        
        self.put()
        
    def flush_and_update_tier_membership_configuration(self, memberships_list):
        
        logger.debug('flush_and_update_tier_membership_configuration: memberships_list count=%d ', len(memberships_list))  
        
        membership_configuration_list = []
        
        for m in memberships_list:
            membership_configuration_list.append(m.to_configuration())
            
        self.tier_membership_configuration = {'memberships':membership_configuration_list, 'count':len(membership_configuration_list)}
        
        self.put()                
        
    def flush_dirty_voucher_configuration(self):
        if self.published_voucher_configuration and len(self.published_voucher_configuration)>0:
            existing_vouchers_list  = self.published_voucher_configuration.get('vouchers')
            new_vouchers_list       = []
            for p in existing_vouchers_list:
                try:
                    program = ndb.Key(urlsafe=p.get('program_key')).get()
                    if program.archived is False:
                        new_vouchers_list.append(p)
                except:
                    pass
            
            self.published_voucher_configuration['vouchers']    = new_vouchers_list
            self.published_voucher_configuration['count']       = len(new_vouchers_list)
            
        else:
            self.published_voucher_configuration = {'vouchers':[], 'count':0}
        
        self.put()    
    
    def update_published_program(self, program_configuration):
        if is_empty(self.published_program_configuration):
            self.published_program_configuration = {
                                                'programs'  :[program_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_program_configuration()
            existing_programs_list  = self.published_program_configuration.get('programs')
            
            program_key = program_configuration.get('program_key')
            index = 0
            for p in existing_programs_list:
                if p.get('program_key') == program_key:
                    existing_programs_list.pop(index)
                
                index = index+1
            
            existing_programs_list.append(program_configuration)
            
            self.published_program_configuration['programs']    = existing_programs_list
            self.published_program_configuration['count']       = len(existing_programs_list) 
            
        self.put()
        
    def update_published_voucher(self, voucher_configuration):
        if is_empty(self.published_voucher_configuration):
            self.published_voucher_configuration = {
                                                'vouchers'  :[voucher_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_program_configuration()
            existing_vouchers_list  = self.published_voucher_configuration.get('vouchers')
            
            voucher_key = voucher_configuration.get('voucher_key')
            
            index = 0
            for v in existing_vouchers_list:
                if v.get('voucher_key') == voucher_key:
                    existing_vouchers_list.pop(index)
                
                index = index+1
            
            existing_vouchers_list.append(voucher_configuration)
            
            self.published_voucher_configuration['vouchers']    = existing_vouchers_list
            self.published_voucher_configuration['count']       = len(existing_vouchers_list) 
            
        self.put() 
        
    def add_membership(self, membership_configuration):
        if is_empty(self.membership_configuration):
            self.membership_configuration = {
                                                'memberships'  :[membership_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_membership_configuration()
            existing_memberships_list  = self.membership_configuration.get('memberships')
            existing_memberships_list.append(membership_configuration)
            
            self.membership_configuration['memberships']     = existing_memberships_list
            self.membership_configuration['count']           = len(existing_memberships_list) 
            
        self.put()
        
    def update_membership(self, membership_configuration):
        if is_empty(self.membership_configuration):
            self.membership_configuration = {
                                                'memberships'  :[membership_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_membership_configuration()
            existing_memberships_list  = self.membership_configuration.get('memberships')
            
            for idx, em in enumerate(existing_memberships_list):
                if em.get('membership_key') == membership_configuration.get('membership_key'):
                    existing_memberships_list[idx] = membership_configuration
                    break
            
            self.membership_configuration['memberships']     = existing_memberships_list 
            
        self.put()     
        
    def add_tier_membership(self, membership_configuration):
        if is_empty(self.tier_membership_configuration):
            self.tier_membership_configuration = {
                                                'memberships'   :[membership_configuration],
                                                'count'         : 1,
                                                } 
                                            
        else:
            self.flush_dirty_tier_membership_configuration()
            existing_memberships_list  = self.tier_membership_configuration.get('memberships')
            existing_memberships_list.append(membership_configuration)
            
            self.tier_membership_configuration['memberships']     = existing_memberships_list
            self.tier_membership_configuration['count']           = len(existing_memberships_list) 
            
        self.put()
        
    def update_tier_membership(self, membership_configuration):
        if is_empty(self.tier_membership_configuration):
            self.tier_membership_configuration = {
                                                'memberships'   :[membership_configuration],
                                                'count'         : 1,
                                                } 
                                            
        else:
            self.flush_dirty_tier_membership_configuration()
            existing_memberships_list  = self.tier_membership_configuration.get('memberships')
            
            for idx, em in enumerate(existing_memberships_list):
                if em.get('membership_key') == membership_configuration.get('membership_key'):
                    existing_memberships_list[idx] = membership_configuration
                    break
            
            self.tier_membership_configuration['memberships']     = existing_memberships_list
            
        self.put()                
        
    def remove_program_from_published_program_configuration(self, program_key_to_remove):
        
        logger.debug('remove_program_from_published_program_configuration: program_key_to_remove=%s', program_key_to_remove)
        
        #self.flush_dirty_program_configuration()
        existing_programs_list  = self.published_program_configuration['programs']
        program_count           = len(existing_programs_list)
        
        logger.debug('program_count before remove=%s', program_count)
        
        index = 0
        
        for program in existing_programs_list:
            
            logger.debug('program_key=%s', program.get('program_key'))
            
            is_same_program_key = program.get('program_key') == program_key_to_remove
            
            logger.debug('is_same_program_key=%s', is_same_program_key)
            
            if is_same_program_key:
                existing_programs_list.pop(index)
                
                logger.debug('Found program to be remove')
                
            index = index+1
        
        program_count = len(existing_programs_list)
        
        logger.debug('program_count after remove=%s', program_count)
        
        self.published_program_configuration['programs']    = existing_programs_list
        self.published_program_configuration['count']       = program_count
            
        self.put() 
        
    def remove_archieve_voucher(self, archieve_voucher_key):
        self.flush_dirty_voucher_configuration()
        existing_vouchers_list = self.published_voucher_configuration['vouchers']
        
        index = 0
        
        for voucher in existing_vouchers_list:
            if voucher.get('voucher_key') == archieve_voucher_key:
                existing_vouchers_list.pop(index)
            index = index+1
        
        self.published_voucher_configuration['vouchers']    = existing_vouchers_list
        self.published_voucher_configuration['count']       = len(existing_vouchers_list)
            
        self.put()
        
    def remove_archieve_basic_membership(self, archieve_membership_key):
        self.flush_dirty_membership_configuration()
        existing_memberships_list = self.membership_configuration['memberships']
        
        index = 0
        
        for m in existing_memberships_list:
            if m.get('membership_key') == archieve_membership_key:
                existing_memberships_list.pop(index)
            index = index+1
        
        self.membership_configuration['memberships']    = existing_memberships_list
        self.membership_configuration['count']       = len(existing_memberships_list)
            
        self.put() 
        
    def remove_archieve_tier_membership(self, archieve_membership_key):
        self.flush_dirty_tier_membership_configuration()
        existing_memberships_list = self.tier_membership_configuration['memberships']
        
        index = 0
        
        for m in existing_memberships_list:
            if m.get('membership_key') == archieve_membership_key:
                existing_memberships_list.pop(index)
            index = index+1
        
        self.tier_membership_configuration['memberships']  = existing_memberships_list
        self.tier_membership_configuration['count']             = len(existing_memberships_list)
            
        self.put()                
    
    def update_stat_details(self, stat_dict):
        dashboard_stat_figure = self.dashboard_stat_figure
        logger.debug('update_stat_figure: dashboard_stat_figure=%s', dashboard_stat_figure)
        
        next_updated_datetime = datetime.now() + timedelta(minutes=int(self.stat_figure_update_interval_in_minutes))
        
        logger.debug('update_stat_figure: next_updated_datetime=%s', next_updated_datetime)
        
        dashboard_stat_figure = {
                                'next_updated_datetime' : next_updated_datetime.strftime(self.stat_figure_update_datetime_format),
                                'stat_details'          : stat_dict,
                             }
            
        self.dashboard_stat_figure = dashboard_stat_figure
        self.put()
    
    def get_stat_details(self):
        dashboard_stat_figure = self.dashboard_stat_figure
        
        logger.debug('get_stat_figure: dashboard_stat_figure=%s', dashboard_stat_figure)
        
        if dashboard_stat_figure is not None and dashboard_stat_figure.get('next_updated_datetime'):
            next_updated_datetime = dashboard_stat_figure.get('next_updated_datetime')
            
            logger.debug('get_stat_figure: next_updated_datetime=%s', next_updated_datetime)
            
            if next_updated_datetime:
                next_updated_datetime = datetime.strptime(next_updated_datetime, self.stat_figure_update_datetime_format)
                now = datetime.now()
                if now > next_updated_datetime:
                    return None
                else:
                    return dashboard_stat_figure.get('stat_details')
        
        return None
    
    @staticmethod
    def create(company_name=None, contact_name=None, email=None, mobile_phone=None, office_phone=None, plan_start_date=None, plan_end_date=None, 
               account_code=None, currency_code=None):
        
        if account_code is None:
            account_code    = "%s-%s-%s-%s" % (random_number(4),random_number(4),random_number(4),random_number(4))
            
        merchant_acct   = MerchantAcct(
                                       company_name     = company_name, 
                                       contact_name     = contact_name,
                                       email            = email,
                                       mobile_phone     = mobile_phone,
                                       office_phone     = office_phone,
                                       plan_start_date  = plan_start_date, 
                                       plan_end_date    = plan_end_date,
                                       currency_code    = currency_code
                                       )
        
        logging.debug('account_code=%s', account_code)
        
        merchant_acct.account_code = account_code
        
        merchant_acct.put()
        
        return merchant_acct
    
    @staticmethod
    def get_by_account_code(account_code):
        return MerchantAcct.query(ndb.AND(MerchantAcct.account_code==account_code)).get()
    
    @staticmethod
    def get_by_api_key(api_key):
        return MerchantAcct.query(ndb.AND(MerchantAcct.api_key==api_key)).get()
        
    
    @staticmethod
    def list(offset=0, limit=10):
        return MerchantAcct.query().order(-MerchantAcct.registered_datetime).fetch(offset=offset, limit=limit)
    
    def delete_and_related(self):
        
        @ndb.transactional()
        def start_transaction(merchant_acct):
            merchant_user_key_list = MerchantUser.list_by_merchant_account(merchant_acct, keys_only=True)
            if merchant_user_key_list:
                ndb.delete_multi(merchant_user_key_list)
            
            merchant_acct.delete()
            logger.debug('after deleted merchant acct and merchant user')
            
        
        start_transaction(self)
        
class MerchantSentEmail(SentEmail):
    '''
    Merchant account as Ancestor
    '''
    pass

class Outlet(BaseNModel, DictModel, FullTextSearchable):
    '''
    Merchant account as Ancestor
    '''
    
    merchant_acct           = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    name                    = ndb.StringProperty(required=True)
    address                 = ndb.StringProperty(required=False)
    office_phone            = ndb.StringProperty(required=False)
    fax_phone               = ndb.StringProperty(required=False)
    email                   = ndb.StringProperty(required=False)
    business_hour           = ndb.StringProperty(required=False)
    is_physical_store       = ndb.BooleanProperty(required=False, default=True)
    geo_location            = ndb.GeoPtProperty(required=False)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    fulltextsearch_field_name   = 'name'
    
    dict_properties         = ['key', 'name', 'address', 'office_phone', 
                                'fax_phone', 'email', 'business_hour', 'is_physical_store', 
                                'geo_location', 'created_datetime']
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def merchant_acct_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    
    @property
    def outlet_key(self):
        return self.key.urlsafe()
    
    @staticmethod
    def create(merchant_acct=None,name=None, address=None, email=None, fax_phone=None, 
               office_phone=None, business_hour=None, geo_location=None, is_physical_store=True):
        
        outlet   = Outlet(
                            parent              = merchant_acct.create_ndb_key(),
                            name                = name, 
                            address             = address,
                            email               = email,
                            fax_phone           = fax_phone,
                            office_phone        = office_phone,
                            business_hour       = business_hour,
                            geo_location        = geo_location,
                            is_physical_store   = is_physical_store,
                            )
        
        outlet.put()
        
        return outlet
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return Outlet.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_all_by_merchant_account(merchant_acct, offset=None, start_cursor=None, return_with_cursor=False, keys_only=False, limit = model_conf.MAX_FETCH_RECORD):
        #condition_query =  Outlet.query(ancestor = merchant_acct.create_ndb_key()).order(-Outlet.created_datetime)
        condition_query =  Outlet.query(ancestor = merchant_acct.create_ndb_key())
        return Outlet.list_all_with_condition_query(
                                        condition_query, 
                                        offset=offset, 
                                        start_cursor=start_cursor, 
                                        return_with_cursor=return_with_cursor, 
                                        keys_only=keys_only, 
                                        limit=limit)
    
    @staticmethod
    def count_by_merchant_account(merchant_acct):
        condition_query = Outlet.query(ancestor = merchant_acct.create_ndb_key())
        return Outlet.count_with_condition_query(condition_query, limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def search_by_merchant_account(name=None, 
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list = None
        query = Outlet.query()
        
        if is_not_empty(name):
            search_text_list = name.split(' ')
            
        total_count                         = Outlet.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = Outlet.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)

class MerchantUser(UserMin, FullTextSearchable):
    
    '''
    parent is MerchantAcct
    '''
    username                = ndb.StringProperty(required=True)
    permission              = ndb.JsonProperty()
    is_admin                = ndb.BooleanProperty(required=True, default=False)
    basic_auth_token        = ndb.StringProperty(required=False)
    
    dict_properties         = ['key', 'user_id', 'name', 'username', 'permission', 'granted_outlet', 'granted_access',
                                'created_datetime', 'active', 'is_admin', 'basic_auth_token', 
                                'is_super_user', 'is_admin_user', 'is_merchant_user']
    
    fulltextsearch_field_name   = 'name'
    
    @property
    def is_super_user(self):
        return False
    
    @property
    def is_admin_user(self):
        return self.is_admin
    
    @property
    def is_merchant_user(self):
        return True
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def merchant_acct_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def granted_outlet(self):
        if self.is_admin:
            logger.debug('is admin merchant user')
            g_outlets_list = []
            all_outlet_list = Outlet.list_by_merchant_acct(self.merchant_acct)
            
            logger.debug('all_outlet_list=%s', all_outlet_list)
            
            for o in all_outlet_list:
                g_outlets_list.append(o.key_in_str)
                
            return g_outlets_list
            
        else:
            if self.permission:
                return self.permission.get('granted_outlet')
            else:
                return []
        
    @property
    def granted_outlet_details_list(self):
        g_outlets_list = []
        
        if self.is_admin:
            logger.debug('is admin merchant user')
            
            all_outlet_list = Outlet.list_by_merchant_acct(self.merchant_acct)
            
            for o in all_outlet_list:
                g_outlets_list.append({
                                        'outlet_key'    : o.key_in_str,
                                        'name'          : o.name,
                                        })
                
            return g_outlets_list
            
        else:
            outlet_key_list =  self.permission.get('granted_outlet')
            
            for o in  outlet_key_list:
                outlet_details = Outlet.fetch(o)
                g_outlets_list.append({
                                        'outlet-key'    : 0,
                                        'name'          : outlet_details.name,
                                        })
        return g_outlets_list
    
    @property
    def granted_access(self):
        if self.permission:
            return self.permission.get('granted_access')
        else:
            return []
    
    @staticmethod
    def update_permission(merchant_user, access_permission, outlet_permission, is_admin=False):
        if access_permission is None:
            access_permission = []
            
        if outlet_permission is None:
            outlet_permission = []
            
        merchant_user.is_admin = is_admin
        merchant_user.permission = {'granted_access': access_permission, 'granted_outlet': outlet_permission}
        merchant_user.put()
    
    @staticmethod
    def create(merchant_acct=None, name=None, 
               username=None,
               password=None):
        
        check_unique_merchant_user = MerchantUser.get_by_username(username)
        
        if check_unique_merchant_user is None:
            user_id = generate_user_id()
            created_user = MerchantUser(
                                parent = merchant_acct.create_ndb_key(),
                                user_id=user_id, 
                                name=name, 
                                username=username
                                )
            
            hashed_password = hash_password(user_id, password)
            created_user.password = hashed_password
                
            created_user.put()
            
            return created_user
        else:
            raise Exception('Username have been used')
    
    @staticmethod
    def count_by_merchant_account(merchant_acct):
        condition_query = MerchantUser.query(ancestor = merchant_acct.create_ndb_key())
        return MerchantUser.count_with_condition_query(condition_query, limit=model_conf.MAX_FETCH_RECORD)  
    
    @staticmethod
    def list_by_merchant_account(merchant_acct, keys_only=False):
        return MerchantUser.query(ancestor = merchant_acct.create_ndb_key()).order(-MerchantUser.created_datetime).fetch(limit=model_conf.MAX_FETCH_RECORD, keys_only=keys_only)
    
    @staticmethod
    def list_all_by_merchant_account(merchant_acct, offset=None, start_cursor=None, return_with_cursor=False, keys_only=False, limit = model_conf.MAX_FETCH_RECORD):
        condition_query =  MerchantUser.query(ancestor = merchant_acct.create_ndb_key()).order(-MerchantUser.created_datetime)
        return MerchantUser.list_all_with_condition_query(
                                        condition_query, 
                                        offset=offset, 
                                        start_cursor=start_cursor, 
                                        return_with_cursor=return_with_cursor, 
                                        keys_only=keys_only, 
                                        limit=limit)
    
    @staticmethod
    def get_by_username(username):
        return MerchantUser.query(ndb.AND(MerchantUser.username==username)).get()
    
    
    @staticmethod
    def get_merchant_acct_by_merchant_user(merchant_user):
        return MerchantUser.fetch(merchant_user.key.parent().urlsafe())
    
    
    @staticmethod
    def search_by_merchant_account(name=None, username=None,
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list = None
        query = MerchantUser.query()
        
        if is_not_empty(name):
            search_text_list = name.split(' ')
            
        elif is_not_empty(username):
            query = query.filter(MerchantUser.username==username)
            
        
        
        total_count                         = MerchantUser.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = MerchantUser.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
    
    
class MerchantTagging(Tagging):    
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None):
        return MerchantTagging.create_tag(parent=merchant_acct.create_ndb_key(), label=label, desc=desc)
    
    def update(self, label=None, desc=None):
        self.label  = label
        self.desc   = desc
        self.put()
        
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        return MerchantTagging.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit = conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def get_by_merchant_label(merchant_acct, label):
        return MerchantTagging.get_by_label(merchant_acct.create_ndb_key(), label)
    
    