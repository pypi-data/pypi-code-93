'''
Created on 25 Jan 2021

@author: jacklok
'''
from trexmodel import conf as model_conf
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel

class UpstreamData(BaseNModel, DictModel):
    table_template_name     = ndb.StringProperty(required=True)
    dataset_name            = ndb.StringProperty(required=True)
    table_name              = ndb.StringProperty(required=True)
    stream_content          = ndb.JsonProperty(required=True)
    is_sent                 = ndb.BooleanProperty(required=True, default=False)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    dict_properties = ['table_template_name', 'dataset_name', 'table_name', 'stream_content', 'is_sent']
    
    @staticmethod
    def list_not_send(offset=0, limit=model_conf.MAX_FETCH_RECORD, start_cursor=None,return_with_cursor=False, keys_only=False):
        query = UpstreamData.query(ndb.AND(UpstreamData.is_sent==False))
        
        return UpstreamData.list_all_with_condition_query(query, offset=offset, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only, limit=limit)
        
    
    @staticmethod
    def count_not_sent(limit=model_conf.MAX_FETCH_RECORD):
        return UpstreamData.query(ndb.AND(UpstreamData.is_sent==False)).count(limit = limit)
    
    @staticmethod
    def create(dataset_name, table_name, table_template_name, stream_content):
        UpstreamData(
                    table_template_name = table_template_name,
                    dataset_name        = dataset_name,
                    table_name          = table_name,
                    stream_content      = stream_content,
                    ).put()
                    

    
    
                    
    
