"""
IBM COS cache for computationally expensive features
"""
import inspect
from botocore.client import Config
import ibm_boto3
import os
import datetime as dt
from collections import OrderedDict
import pickle as pl

from ibm_botocore import config
from dimsum.utility.cache_functions import *
from dimsum.providers.cache.cache_registry_base import CacheRegistryBase

class IBMObjectStorageCacheRegistry(CacheRegistryBase):
    _UID = 'uid'

    def __init__(self, config):
        # User defined config
        self.config = config
        self.IBM_API_KEY_ID = config['ibm_api_key_id']
        self.ENDPOINT = config['endpoint']
        self.IBM_AUTH_ENDPOINT = "https://iam.ng.bluemix.net/oidc/token"
        if 'ibm_auth_endpoint' in config:   
            self.IBM_AUTH_ENDPOINT = config['ibm_auth_endpoint']
        self.BUCKET = config['bucket']
        self.cache_filename = config['object_name']
        self.client = self.__get_boto_client__()
        self.capacity = config['capacity']

    def get(self, key, **kwargs):
        try: 
            cache_registry = self.get_cache_registry()
            dataset_reference = cache_registry.get(key)
        
            if dataset_reference is None:
                return None
            dataset_is_removed = is_expired(dataset_reference)

            if dataset_is_removed:
                cache_registry.pop(key)
                self.__save_cache_registry__(cache_registry)
                return None
            
            cache_registry.move_to_end(key)
            self.__save_cache_registry__(cache_registry)
            # return and get dataset from persistor
            return dataset_reference.get(IBMObjectStorageCacheRegistry._UID)
        except Exception as e:
            print('> cache registry "get" operation failed!\n', e)
        return None
        

    def put(self, key, uid, **kwargs):
        if (self.capacity == 0): return
        try:
            cache_registry = self.get_cache_registry()
            dataset = cache_registry.get(key)
            if dataset is None:
                evicted = None
                if len(cache_registry) >= self.capacity:
                    remove_all_expired(cache_registry)
                    if len(cache_registry) >= self.capacity:
                        # Need key to determine which dataset node to evict
                        evicted = cache_registry.popitem(last=False)[1]
                        
                cache_registry[key] = create_dataset_reference(uid, **kwargs)
                self.__save_cache_registry__(cache_registry)

                if evicted is not None:
                    return evicted.get(IBMObjectStorageCacheRegistry._UID), True
                else:
                    return None, True
        except Exception as e:
            print('> cache registry "put" operation failed!\n', e)
        return None, False
    
    def delete(self, *keys):
        try:
            cache_registry = self.get_cache_registry()
            count = 0
            for key in keys:
                if cache_registry.pop(key, None) is not None:
                    count += 1

            if count > 0:
                self.__save_cache_registry__(cache_registry)
            return count
        except Exception as e:
            print('> cache registry "delete" operation failed!\n', e)

    def stats(self, **kwargs):
        pass

    """
    "   Read the cache dumps and deserialize it
    """
    def get_cache_registry(self):
        """
        return the cache dictionary
        """
        cache_registry = OrderedDict()
        filename = f'{self.cache_filename}.dill'
        try:
            body = self.client.get_object(Bucket=self.BUCKET,Key=filename)['Body']
            bytes_obj = body.read()
            cache_registry = pl.loads(bytes_obj)
        except Exception as e:
            print('> Cache registry not found!\n', e)
            raise
        return OrderedDict(cache_registry)
    
    """
    "   Serializes the cache and saves it to the IBM COS
    """
    def __save_cache_registry__(self, new_cache):
        """
        @param::new_cache: cache object containing collection of cached datasets
        return None
        """
        filename = f'{self.cache_filename}.dill'
        try:
            if new_cache == None:
                raise Exception('> save_cache_to_storage: (new)cache can not be None!')
            if not isinstance(new_cache, dict):
                raise Exception('> save_cache_to_storage: (new)cache is not dictionary type!')

            dumps = pl.dumps(new_cache)
            self.client.put_object(ACL='public-read', Body=dumps, Bucket=self.BUCKET, Key=filename)
        except Exception as e:
            print('"save_cache_to_storage" operation failed!\n', e)
            raise

    def __get_boto_client__(self):
        """
        @param::none:
        return the ibm boto client instance
        """
        client = None
        try:
            client = ibm_boto3.client(service_name='s3',
                                    ibm_api_key_id=self.IBM_API_KEY_ID,
                                    ibm_auth_endpoint=self.IBM_AUTH_ENDPOINT,
                                    config=Config(signature_version='oauth'),
                                    endpoint_url=self.ENDPOINT)
        except Exception as e:
            print('> ibm boto client initialization failed! \n', e)

        return client
