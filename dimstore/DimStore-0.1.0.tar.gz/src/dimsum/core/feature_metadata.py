import uuid
from datetime import datetime

"""
"  use dictionary instead of class attributes enable deserialization backward compatibility,
"  add new meta data member will still be able to deserialize from old object dumps.
"  !important idea is to keep this poco object as simple as possible to enable the backward 
"  compatibility of serialization/deserialization process.
"""

class FeatureOperation():
    CREATE = 1
    CREATE_NEW_VERSION = 2
    UPDATE = 3
    DELETE = 4

class FeatureMetaBase(object):
    
    def __init__(self):
        self.metadata = {}

class FeatureMetaData(FeatureMetaBase):

    def __init__(self, name, index, output, namespace = 'default'):
        super().__setattr__('metadata', 
                                                {
                                                    'uid': str(uuid.uuid4()),
                                                    'name': name,
                                                    'index': index,
                                                    'namespace': namespace,
                                                    'author':"",
                                                    'tags': set([]),
                                                    'params':{},
                                                    'output':output,
                                                    'comment':'',
                                                    'create_date': datetime.today(),
                                                    'versioning': False,
                                                    'latest_version': 0
                                                })

    def __getattr__(self,key):
        if key in self.metadata:
            return self.metadata[key]
        else:
            return None

    def __setattr__(self,key,value):
        # todo: sanity check the value, make sure the value is valid for the meta attributes
        self.metadata[key] = value

    def __getstate__(self): 
        return self.__dict__

    def __setstate__(self, d): 
        self.__dict__.update(d)
      

