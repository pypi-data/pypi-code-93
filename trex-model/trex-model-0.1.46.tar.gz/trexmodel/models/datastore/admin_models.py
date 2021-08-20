'''
Created on 8 May 2020

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.user_models import UserMin
from trexlib.utils.security_util import generate_user_id, hash_password


class SuperUser(UserMin):
    email                           = ndb.StringProperty(required=False)
    created_datetime                = ndb.DateTimeProperty(required=False, auto_now_add=True)
    
    dict_properties         = ['user_id', 'name', 'email', 'gravatar_url', 'active', 'locked', 
                               'is_super_user', 'is_admin_user', 'is_merchant_user', 'created_datetime']
    
    @property
    def is_super_user(self):
        return True
    
    @property
    def is_admin_user(self):
        return False
    
    @property
    def is_merchant_user(self):
        return False
    
    @classmethod
    def new_super_user_id(cls):
        return 'superuser'
    
    @classmethod
    def create(cls, name=None, email=None, password=None, active=False):
        
        user_id = cls.new_super_user_id()
        created_user = cls(user_id=user_id, name=name, email=email, active=active)
        
        hashed_password         = hash_password(user_id, password)
        created_user.password   = hashed_password
            
        created_user.put()
        return created_user
    
    @classmethod
    def list(cls, offset=0, limit=10):
        return cls.query().order(-cls.joined_date).fetch(offset=offset, limit=limit)
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query(ndb.AND(cls.email==email)).get()
    
class AdminUser(SuperUser):
    permission              = ndb.JsonProperty()
    is_superuser            = ndb.BooleanProperty(required=True, default=False)
    dict_properties         = ['user_id', 'name', 'email', 'gravatar_url', 'active', 'locked', 
                               'permission', 'is_superuser', 'is_super_user', 'is_admin_user', 'is_merchant_user', 'created_datetime']
    
    @classmethod
    def new_super_user_id(cls):
        return generate_user_id()
    
    @property
    def is_super_user(self):
        return self.is_superuser
    
    @property
    def is_admin_user(self):
        return True
    
    @property
    def is_merchant_user(self):
        return False
    
    @staticmethod
    def update_permission(admin_user, permission, is_superuser=False):
        admin_user.is_superuser = is_superuser
        admin_user.permission = {'granted_access': permission}
        admin_user.put()

