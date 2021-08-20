'''
Created on 10 Apr 2020

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
#from trexlib.utils.common.cache_util import cache
from trexlib.utils.string_util import random_number, is_not_empty
from flask_login import UserMixin
import logging  
from trexlib.utils.security_util import generate_user_id, hash_password

from trexlib import conf as lib_conf
from trexmodel import conf as model_conf
import json
from json import JSONEncoder
from flask_babel import gettext

logger = logging.getLogger("model")

class UserMin(BaseNModel, DictModel, UserMixin):
    
    #system internal usage
    user_id                     = ndb.StringProperty(required=True)
    password                    = ndb.StringProperty(required=False)
    gravatar_url                = ndb.StringProperty(required=False)
    
    #---------------------------------------------------------------------------
    # User Personal Details
    #---------------------------------------------------------------------------
    name                        = ndb.StringProperty(required=False)
    reset_password_reminder     = ndb.BooleanProperty(required=False, default=False)
    
    created_datetime            = ndb.DateTimeProperty(required=False, auto_now_add=True)
    last_login_datetime         = ndb.DateTimeProperty(required=False)

    locked                      = ndb.BooleanProperty(required=False, default=False)
    active                      = ndb.BooleanProperty(required=True, default=True)
    try_count                   = ndb.IntegerProperty(required=False)
    
    dict_properties             = ['user_id', 'name', 'email', 'gravatar_url', 'active', 'locked']
    
    @classmethod
    #@cache.memoize(timeout=60)
    def get_by_user_id(cls, user_id):
        logger.debug('UserMin.get_by_user_id: read from database')
        return cls.query(cls.user_id==user_id).get()
    
    def get_id(self):
        return self.user_id
    
    @property
    def is_super_user(self):
        return False
    
    @property
    def is_admin_user(self):
        return False
    
    def is_valid_password(self, checking_password):
        hashed_signin_password = hash_password(self.user_id, checking_password)
        
        logger.debug('is_valid_password: checking_password=%s', checking_password)
        logger.debug('is_valid_password: hashed_signin_password=%s', hashed_signin_password)
        logger.debug('is_valid_password: user password=%s', self.password)
        
        is_signin_password_valid = hashed_signin_password == self.password
        
        logger.debug('is_valid_password: is_signin_password_valid=%s', is_signin_password_valid)
        
        return is_signin_password_valid
    
class Role(BaseNModel):
    id              = ndb.StringProperty(required=True)
    name            = ndb.StringProperty(required=True)
    description     = ndb.TextProperty(required=False)


class UserBase(UserMin):
    #---------------------------------------------------------------------------
    # User System Generated fields
    #---------------------------------------------------------------------------
    reference_code              = ndb.StringProperty(required=True)
    
    #---------------------------------------------------------------------------
    # User Mutual Mandatory fields
    #---------------------------------------------------------------------------
    email                       = ndb.StringProperty(required=False)
    mobile_phone                = ndb.StringProperty(required=False)
    
    #---------------------------------------------------------------------------
    # User Personal Details
    #---------------------------------------------------------------------------
    birth_date                  = ndb.DateProperty(required=False, indexed=False) 
    birth_date_date_str         = ndb.StringProperty(required=False)
    gender                      = ndb.StringProperty(required=False, choices=set([
                                                                    model_conf.GENDER_MALE_CODE, 
                                                                    model_conf.GENDER_FEMALE_CODE
                                                                    ]))
    national_id                 = ndb.StringProperty(required=False, )
    
    #---------------------------------------------------------------------------
    # User Contact Details
    #---------------------------------------------------------------------------
    
    country                     = ndb.StringProperty(required=False, default=lib_conf.DEFAULT_COUNTRY_CODE)
    state                       = ndb.StringProperty(required=False)
    city                        = ndb.StringProperty(required=False, )
    postcode                    = ndb.StringProperty(required=False, )
    address                     = ndb.StringProperty(required=False, )
    
    #---------------------------------------------------------------------------
    # User account activation required fields
    #---------------------------------------------------------------------------
    is_email_verified           = ndb.BooleanProperty(required=False, default=False)
    is_mobile_phone_verified    = ndb.BooleanProperty(required=False, default=False)

    modified_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)
    
    @property
    def age(self):
        if self.birth_date:
            from dateutil.relativedelta import relativedelta
            from datetime import date
            today   = date.today()
            __age   = relativedelta(today, self.birth_date)
            return __age.years
        else:
            return 0
    
    @classmethod
    def get_by_email(cls, email):
        return User.query(ndb.AND(User.email==email)).get()
        
    @classmethod
    def get_by_mobile_phone(cls, mobile_phone):
        return User.query(ndb.AND(User.mobile_phone==mobile_phone)).get()
    
    @classmethod
    def create(cls, name=None, email=None, mobile_phone=None, 
               gender=None, birth_date=None, 
               password=None):
        
        user_id             = generate_user_id()
        reference_code      = random_number(16) 
        birth_date_date_str = None
        
        if birth_date:
            birth_date_date_str = birth_date.strftime('%d/%m')
            
        if mobile_phone:
            mobile_phone = mobile_phone.replace(" ", "")    
        
        created_user = cls(user_id=user_id, name=name, email=email, mobile_phone=mobile_phone, 
                           gender=gender, birth_date=birth_date, birth_date_date_str=birth_date_date_str, 
                           reference_code=reference_code
                           )
        
        hashed_password = hash_password(user_id, password)
        created_user.password = hashed_password
            
        created_user.put()
        
        return created_user
    
    @classmethod
    def update(cls, user_acct=None, **kwargs):
        logger.debug('**kwargs=%s', kwargs)
        
        mobile_phone    = kwargs.get('mobile_phone')
        password        = kwargs.get('password')
        
        if mobile_phone:
            mobile_phone = mobile_phone.replace(" ", "")
        
        kwargs['mobile_phone'] = mobile_phone
        
        for key, value in kwargs.items():
            setattr(user_acct, key, value)
        
        if password:
            hashed_password = hash_password(user_acct.user_id, password)
            user_acct.password = hashed_password
        
        user_acct.put()
        
        return user_acct
        
    
    @classmethod
    def update_contact(cls, user_acct, address=None, city=None, state=None, postcode=None, country=None):
        user_acct.address    = address
        user_acct.city       = city
        user_acct.state      = state
        user_acct.postcode   = postcode
        user_acct.country    = country
        user_acct.put()
        
    @classmethod
    def update_biodata(cls, user_acct, gender=None, birth_date=None):
        user_acct.gender        = gender
        user_acct.birth_date    = birth_date
        birth_date_date_str     = None
        if birth_date:
            birth_date_date_str = birth_date.strftime('%d/%m')
        
        user_acct.birth_date_date_str    = birth_date_date_str
        
        user_acct.put()    
        
class User(UserBase):
    redeem_pin               = ndb.StringProperty(required=False)
    
    dict_properties            = [
                                    'mobile_phone', 'email', 'password', 'name', 'birth_date', 'gender',
                                    'reference_code', 'country', 'state', 'city', 'postcode', 
                                    'address', 'redeem_pin'

                                    ]

    #unique_attributes = 'email,username'

    audit_properties            = [
                                    'mobile_phone', 'email', 'password', 'name', 'birth_date', 'gender',
                                    'reference_code', 'country', 'state', 'city', 'postcode', 
                                    'address', 'redeem_pin'

                                    ]

    unicode_properties = ['name', 'address', 'city']

    export_properties = (
        ('User Id','user_id'),
        ('Name','name'),
        ('Reference Code','reference_code'),
        ('Mobile Phone','mobile_phone'),
        ('Email','email'),
        ('Gender','gender'),
        ('Date of Birth','birth_date'),
        ('Country','country_desc'),
        ('State','state_desc'),
        ('City','city'),
        ('Address','address'),
        ('Registered Datetime','created_datetime'),

    )

    def __repr__(self):
        return '''
                User[key=%s, 
                name=%s, 
                email=%s, 
                mobile_phone=%s, 
                country=%s, 
                locked=%s,
                active=%s
                ]
                ''' % (self.key_in_str, self.name, self.email, self.mobile_phone, self.country, self.locked, self.active)

    
        
    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        logger.info('calling is_active')
        return self.active

      
class LoggedInUser(UserMixin, DictModel):
    
    def __init__(self, json_object, is_super_user=False, is_admin_user=False, is_merchant_user=False):
        
        logging.debug('json_object=%s', json_object)
        
        self.user_id            = json_object.get('user_id') 
        self.name               = json_object.get('name')
        self.email              = json_object.get('email')
        self.gravatar_url       = json_object.get('gravatar_url')
        self.active             = json_object.get('active')
        self.locked             = json_object.get('locked')
        self.permission         = json_object.get('permission')
        self.is_super_user      = json_object.get('is_super_user') or is_super_user
        self.is_admin_user      = json_object.get('is_admin_user') or is_admin_user
        self.is_merchant_user   = json_object.get('is_merchant_user') or is_merchant_user
        self.permission         = json_object.get('permission')
        
        self.show_key_in_dict   = False
        
        self.dict_properties     = ['user_id', 'name', 'gravatar_url', 'active', 'locked', 
                                    'is_super_user', 'is_admin_user', 'is_merchant_user', 'permission']
        
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return self.active
    
    @property
    def is_anonymous(self):
        return False    

    
