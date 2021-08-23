import os
from os.path import expanduser
from tinydb import TinyDB, Query, where
from tinydb.storages import JSONStorage


class Repository:

    CREDENTIALS         = "CREDENTIALS"
    CONFIG              = "CONFIG"
    ROLE                = "ROLE"
    DB_CREDENTIALS_FILE = os.path.join(expanduser("~"),".awsee","cred")
    DB_CONFIG_FILE      = os.path.join(expanduser("~"),".awsee","cfg")
    DB_ROLE_FILE        = os.path.join(expanduser("~"),".awsee","role")
    DB_MFA_FILE         = os.path.join(expanduser("~"),".awsee","mfa")

    def __init__(self, _dbFile):
        self.database = TinyDB(_dbFile, indent=4)
    
    def isEmpty(self):
        return not len(self.database.all()) > 0
    
    def insert(self, record):
        self.database.insert(record)
    
    def remove(self, query):
        self.database.remove(query)

    def findByProfile(self, profile):
        return self.database.get(Query().profile == profile)
    
    def searchByQuery(self, query):
        return self.database.search(query)
    
    def update(self, record, profile):
        self.database.update(record, Query().profile == profile)
    
    def all(self):
        return self.database.all()
    
    def purge(self):
        self.database.truncate()
    
    def databaseConnection(self):
        return self.database

class CredentialsRepository(Repository):
     def __init__(self):
         super().__init__(Repository.DB_CREDENTIALS_FILE)

class ConfigRepository(Repository):
     def __init__(self):
         super().__init__(Repository.DB_CONFIG_FILE)

class RoleRepository(Repository):
     def __init__(self):
         super().__init__(Repository.DB_ROLE_FILE)

class MfaRepository(Repository):
     def __init__(self):
         super().__init__(Repository.DB_MFA_FILE)




