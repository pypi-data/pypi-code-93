'''
Created on 19 Feb 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
from trexmodel.models.datastore.system_models import SentEmail
from trexmodel.models.datastore.user_models import UserMin
import trexmodel.conf as model_conf
from trexlib.utils.security_util import generate_user_id, hash_password
from trexlib.utils.string_util import random_number
import logging
from datetime import datetime, timedelta
from trexlib.utils.common.date_util import parse_datetime
from trexmodel import conf
from google.auth._default import default
from trexmodel.models.datastore.system_models import Tagging


logger = logging.getLogger('model')

class CorporateBase(BaseNModel, DictModel, FullTextSearchable):
    
    company_name            = ndb.StringProperty(required=True)
    contact_name            = ndb.StringProperty(required=False)
    address                 = ndb.StringProperty(required=False)
    office_phone            = ndb.StringProperty(required=False)
    mobile_phone            = ndb.StringProperty(required=False)
    fax_phone               = ndb.StringProperty(required=False)
    email                   = ndb.StringProperty(required=False)
    country                 = ndb.StringProperty(required=False, default='my')
    status                  = ndb.StringProperty(required=False)
    
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    registered_datetime     = ndb.DateTimeProperty(required=True, auto_now_add=True)
    plan_start_date         = ndb.DateProperty(required=True)
    plan_end_date           = ndb.DateProperty(required=True)
    
    fulltextsearch_field_name   = 'company_name'
    
    

class CorporateAcct(CorporateBase):
    account_code                = ndb.StringProperty(required=False)
    logo_public_url             = ndb.StringProperty(required=False)
    logo_storage_filename       = ndb.StringProperty(required=False)
    dashboard_stat_figure       = ndb.JsonProperty()
    currency_code               = ndb.StringProperty(required=False, default='myr')
    
    
    