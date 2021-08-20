'''
Created on 19 Feb 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet,\
    MerchantUser
from trexmodel.models.datastore.coporate_models import CorporateAcct
import logging
from trexlib.utils.common.cache_util import cache
from trexmodel import conf, program_conf
from datetime import datetime


logger = logging.getLogger('model')


class ProgramBase(BaseNModel, DictModel):
    reward_base                         = ndb.StringProperty(required=True, choices=set(program_conf.REWARD_BASE_SET))
    reward_format                       = ndb.StringProperty(required=False, choices=set(program_conf.REWARD_FORMAT_SET))
    completed_status                    = ndb.StringProperty(required=True, choices=set(program_conf.PROGRAM_STATUS))
    giveaway_method                     = ndb.StringProperty(required=False, default=program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM)
    start_date                          = ndb.DateProperty(required=True)
    end_date                            = ndb.DateProperty(required=True)
    desc                                = ndb.StringProperty(required=False)
    program_settings                    = ndb.JsonProperty(required=True)
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    published_datetime                  = ndb.DateTimeProperty(required=False)
    archived_datetime                   = ndb.DateTimeProperty(required=False)
    
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    enabled                             = ndb.BooleanProperty(default=True)
    archived                            = ndb.BooleanProperty(default=False)
    
    @property
    def is_enabled(self):
        return self.enabled
    
    @property
    def is_disabled(self):
        return self.enabled==False
    
    @property
    def is_archived(self):
        return self.archived
    
    @property
    def is_published(self):
        return self.completed_status == program_conf.PROGRAM_STATUS_PUBLISH
    
    @property
    def is_review_state(self):
        return program_conf.is_existing_program_status_final_state(self.completed_status)
    
    @property
    def completed_prograss_in_percentage(self):
        return program_conf.program_completed_progress_percentage(self.completed_status)
    
    @property
    def completed_status_index(self):
        return program_conf.get_program_completed_status_index(self.completed_status)
    
    @property
    def spending_currency(self):
        return self.program_settings.get('scheme').get('spending_currency')
    
    @property
    def reward_amount(self):
        return self.program_settings.get('scheme').get('reward_amount')
    
    @property
    def is_reward_amount_required(self):
        return self.reward_base!=program_conf.REWARD_FORMAT_VOUCHER
    
    @property
    def is_multitier_scheme(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('is_multitier_scheme') or False
    
    @property
    def is_multitier_membership(self):
        return self.program_settings and self.program_settings.get('is_multitier_membership')
        
    @property
    def is_recurring_scheme(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('is_recurring_scheme') or True
        
    @property
    def expiration_type(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_type')
        
    @property
    def is_expiration_date_type(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_type') == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE    
        
    @property
    def expiration_date(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_date')
        
    @property
    def expiration_value(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_value')                
    
    
    @property
    def exclusive_tags_list(self):
        if self.program_settings.get('exclusivity') and self.program_settings.get('exclusivity').get('tags'):
            return ','.join(self.program_settings.get('exclusivity').get('tags')) or ''
        
    @property
    def exclusive_memberships_list(self):
        if self.program_settings.get('exclusivity') and self.program_settings.get('exclusivity').get('memberships'):
            return ','.join(self.program_settings.get('exclusivity').get('memberships')) or ''
        
    @property
    def exclusive_tier_memberships_list(self):
        if self.program_settings.get('exclusivity') and self.program_settings.get('exclusivity').get('tier_memberships'):
            return ','.join(self.program_settings.get('exclusivity').get('tier_memberships')) or ''        
    
    def to_program_configuration(self):
        program_configuration = {
                                'program_key'                       : self.key_in_str,
                                'desc'                              : self.desc,
                                'reward_base'                       : self.reward_base,
                                'reward_format'                     : self.reward_format,
                                'giveaway_method'                   : self.giveaway_method,
                                'start_date'                        : self.start_date.strftime('%d-%m-%Y'),
                                'end_date'                          : self.end_date.strftime('%d-%m-%Y'),    
                                'program_settings'                  : self.program_settings,
                                'is_published'                      : self.is_published,   
                                }
        
        return program_configuration
    
    @classmethod
    def update_program_base_data(cls, program, reward_base=None, reward_format=None, giveaway_method=None, 
                                 giveaway_system_condition = None, giveaway_system_condition_membership_key=None, 
                                 giveaway_system_condition_tier_membership_key=None,
                                 desc=None,start_date=None, end_date=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings = program.program_settings or {}
        
        giveaway_system_settings = program_settings.get('giveaway_system_settings')
        
        if giveaway_system_settings is None:        
            giveaway_system_settings = {
                                                'giveaway_system_condition': giveaway_system_condition
                                            }
        else:
            giveaway_system_settings['giveaway_system_condition'] = giveaway_system_condition
            
        if is_not_empty(giveaway_system_condition_membership_key):
            giveaway_system_settings['giveaway_memberships'] = giveaway_system_condition_membership_key.split(',')
        
        if is_not_empty(giveaway_system_condition_tier_membership_key):
            giveaway_system_settings['giveaway_tier_memberships'] = giveaway_system_condition_tier_membership_key.split(',')
        
        logger.debug('######################## giveaway_system_settings=%s', giveaway_system_settings)
        
        program_settings['giveaway_system_settings'] = giveaway_system_settings
        
        exclusivity_configuration = {
                                                    'tags'              : [],
                                                    'memberships'       : [],
                                                    'tier_memberships'  : [],
                                                    }
        
        program_settings['exclusivity'] = exclusivity_configuration
        
        program.reward_base            = reward_base
        program.reward_format          = reward_format
        program.giveaway_method        = giveaway_method
        program.desc                   = desc
        program.start_date             = start_date
        program.end_date               = end_date
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.completed_status       = program_conf.PROGRAM_STATUS_REWARD_BASE
        program.program_settings       = program_settings
        
        
        
        program.put()
        
        return program
    '''
    @classmethod
    def update_prorgram_reward_format_data(cls, program, reward_format=None, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program.reward_format          = reward_format
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.completed_status       = program_conf.PROGRAM_STATUS_REWARD_FORMAT
        
        
        program.put()
        
        return program
    '''
    @classmethod
    def update_prorgram_reward_scheme_data(cls, program, reward_scheme_configuration={}, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            program_settings = {
                            'scheme'                : [reward_scheme_configuration]
                            }
            
        else:
            program_settings = program.program_settings
            program_settings['scheme']              = reward_scheme_configuration
                
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.completed_status       = program_conf.PROGRAM_STATUS_REWARD_SCHEME
        program.program_settings       = program_settings
        
        
        program.put()
        
        return program
    
    
    @classmethod
    def add_program_voucher(cls, program, voucher_configuration, modified_by=None):
        
        modified_by_username = None
        
        voucher_configuration_list = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            voucher_configuration_list  = []
            program_settings            = {}
            
        else:
            program_settings = program.program_settings
            voucher_configuration_list = program_settings.get('reward_items') or []
            
        
        voucher_configuration_list.append(voucher_configuration)
        program_settings['reward_items']    = voucher_configuration_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        
        program.put()
        
        return program
    
    @classmethod
    def add_program_tier_membership(cls, program, membership_configuration, modified_by=None):
        
        modified_by_username = None
        
        membership_configuration_list = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            membership_configuration_list  = []
            program_settings            = {}
            
        else:
            program_settings = program.program_settings
            membership_configuration_list = program_settings.get('tier_memberships') or []
            
        
        membership_configuration_list.append(membership_configuration)
        
        program_settings['tier_memberships']    = membership_configuration_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        
        program.put()
        
        return program
    
    @classmethod
    def add_program_membership(cls, program, membership_configuration, modified_by=None):
        
        modified_by_username = None
        
        membership_configuration_list = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            membership_configuration_list   = []
            program_settings                = {}
            
        else:
            program_settings = program.program_settings
            membership_configuration_list = program_settings.get('memberships') or []
            
        
        membership_configuration_list.append(membership_configuration)
        
        program_settings['memberships']    = membership_configuration_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        
        program.put()
        
        return program
    
    @classmethod
    def update_prorgram_membership_type_data(cls, program, is_multitier_membership=False, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings = program.program_settings
        program_settings['is_multitier_membership'] = is_multitier_membership
            
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        program.put()
        
        return program
    
    @classmethod
    def update_prorgram_exclusivity_data(cls, program, exclusivity_configuration={}, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings = program.program_settings
        program_settings['exclusivity'] = exclusivity_configuration
            
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.completed_status       = program_conf.PROGRAM_STATUS_REWARD_EXCLUSIVITY
        program.program_settings       = program_settings
        
        program.put()
        
        return program
    
    @property
    def reward_items(self):
        return self.program_settings.get('reward_items')
    
    @property
    def exclusivity_configuration(self):
        return self.program_settings.get('exclusivity')
    
    @classmethod
    def remove_program_voucher(cls, program, voucher_index, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings            = program.program_settings
        program_voucher_listing     = program_settings.get('reward_items')
        
        index = 0
        
        for voucher in program_voucher_listing:
            if voucher.get('voucher_index') == voucher_index:
                program_voucher_listing.pop(index)
                break
            
            index = index +1
    
        program_settings['reward_items']    = program_voucher_listing      
        program.program_settings            = program_settings
        program.modified_by                 = modified_by.create_ndb_key()
        program.modified_by_username        = modified_by_username
        program.put()
        
    @classmethod
    def remove_program_tier_membership(cls, program, membership_key, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings            = program.program_settings
        tier_membership_listing     = program_settings.get('tier_memberships')
        
        index = 0
        
        for membership in tier_membership_listing:
            if membership.get('membership_key') == membership_key:
                tier_membership_listing.pop(index)
                break
            
            index = index +1
    
        program_settings['tier_memberships']    = tier_membership_listing      
        program.program_settings                = program_settings
        program.modified_by                     = modified_by.create_ndb_key()
        program.modified_by_username            = modified_by_username
        program.put()    
        
    @classmethod
    def publish_program(cls, program):
        program.completed_status = program_conf.PROGRAM_STATUS_PUBLISH
        program.published_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct
        merchant_acct.update_published_program(program.to_program_configuration())
        
    @classmethod
    def archive_program(cls, program):
        program.archived = True
        program.archived_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct
        merchant_acct.remove_program_from_published_program_configuration(program.key_in_str)    
    
    @classmethod
    def enable(cls, program):
        program.enabled = True
        program.put()
        
        if program.is_published:
            merchant_acct = program.merchant_acct
            merchant_acct.update_published_program(program.to_program_configuration())
            
        
    @classmethod
    def disable(cls, program):
        program.enabled = False
        program.put()  
        
        merchant_acct = program.merchant_acct
        merchant_acct.remove_program_from_published_program_configuration(program.key_in_str)
    
class MerchantProgram(ProgramBase):
    #merchant_acct           = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct) 
    
    
    dict_properties                     = ['reward_base', 'giveaway_method', 'reward_format', 'completed_status', 'start_date', 'end_date', 'desc', 'program_settings', 
                                           'created_datetime', 'modified_datetime',  'enabled','completed_status','is_enabled', 'is_disabled', 'is_review_state', 
                                           'is_published', 'archived', 'is_reward_amount_required', 'completed_prograss_in_percentage', 'completed_status_index',
                                           'exclusive_tags_list', 'exclusive_memberships_list', 'exclusive_tier_memberships_list',
                                           'is_recurring_scheme', 'is_multitier_scheme', 'is_multitier_membership',
                                           'expiration_type', 'expiration_date', 'expiration_value', 'is_expiration_date_type',
                                           'giveaway_system_condition', 'giveaway_system_condition_memberships_list', 'giveaway_system_condition_tier_memberships_list',
                                           'created_by_username', 'modified_by_username']
    
    @property
    def giveaway_system_condition(self):
        if self.program_settings and self.program_settings.get('giveaway_system_settings'):
            return self.program_settings.get('giveaway_system_settings').get('giveaway_system_condition')
    
    @property
    def giveaway_system_condition_memberships_list(self):
        if self.program_settings and self.program_settings.get('giveaway_system_settings'):
            return self.program_settings.get('giveaway_system_settings').get('giveaway_memberships')
    
    @property
    def giveaway_system_condition_tier_memberships_list(self):
        if self.program_settings and self.program_settings.get('giveaway_system_settings'):
            return self.program_settings.get('giveaway_system_settings').get('giveaway_tier_memberships')
    
    @staticmethod
    def create(merchant_acct, reward_base=None, giveaway_method=None, giveaway_system_condition=None, reward_format=None, 
               giveaway_system_condition_membership_key=None, giveaway_system_condition_tier_membership_key=None,
               desc=None, start_date=None, end_date=None, created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
                
        giveaway_system_settings = {
                                                'giveaway_system_condition': giveaway_system_condition
                                            }
        
        if is_not_empty(giveaway_system_condition_membership_key):
            giveaway_system_settings['giveaway_memberships'] = giveaway_system_condition_membership_key.split(',')
        
        if is_not_empty(giveaway_system_condition_tier_membership_key):
            giveaway_system_settings['giveaway_tier_memberships'] = giveaway_system_condition_tier_membership_key.split(',')
        
        exclusivity_configuration = {
                                                    'tags'              : [],
                                                    'memberships'       : [],
                                                    'tier_memberships'  : [],
                                                    }
        
        program_settings = {
                            'giveaway_system_settings'  : giveaway_system_settings,
                            'exclusivity'               : exclusivity_configuration
                            }
        
        
        
        merchant_program =  MerchantProgram(
                                        parent                              = merchant_acct.create_ndb_key(),
                                        reward_base                         = reward_base,
                                        giveaway_method                     = giveaway_method,
                                        reward_format                       = reward_format,
                                        desc                                = desc,
                                        start_date                          = start_date,
                                        end_date                            = end_date,
                                        created_by                          = created_by.create_ndb_key(),
                                        created_by_username                 = created_by_username,
                                        completed_status                    = program_conf.PROGRAM_STATUS_REWARD_BASE,
                                        program_settings                    = program_settings,
                                        )
        
        merchant_program.put()
        return merchant_program
    
    
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
      
    
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        return MerchantProgram.query(ndb.AND(MerchantProgram.archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_archived_by_merchant_account(merchant_acct):
        return MerchantProgram.query(ndb.AND(MerchantProgram.archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)

class BrandProgram(ProgramBase): 
    #corporate_acct           = ndb.KeyProperty(name="corporate_acct", kind=CorporateAcct)
    pass


           


