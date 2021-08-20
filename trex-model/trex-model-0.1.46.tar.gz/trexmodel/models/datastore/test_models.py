'''
Created on 16 May 2021

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

class TestModelBase(BaseNModel, DictModel):
    id                      = ndb.IntegerProperty(required=True, default=1)
    value                   = ndb.StringProperty(required=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    
    @classmethod
    def create(cls, id=1, value='1'):
        test_model = cls(id=id, value=value)
        test_model.put()

    @classmethod
    def get_by_id(cls, id):
        return cls.query(cls.id==id).get()

class TestModelA(TestModelBase):
    pass

        
class TestModelB(TestModelBase):
    pass      