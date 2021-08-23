"""
    default way to serialize the feature extraction pipeline
"""

import dill
from dimsum.providers.serializer.serializer_base import SerializerBase

class DillSerializer(SerializerBase):
    
    def __init__(self, config):
        self.config = config
        self.nrecurse = False 
        if 'nrecurse' in self.config:
            self.nrecurse = self.config['nrecurse']

    def encode(self, obj, **kwargs):
        dill.settings['recurse'] = self.nrecurse
        dumps = dill.dumps(obj)
        return dumps

    def decode(self, dumps, **kwargs):
        dill.settings['recurse'] = self.nrecurse
        pipeline = dill.loads(dumps)
        return pipeline


