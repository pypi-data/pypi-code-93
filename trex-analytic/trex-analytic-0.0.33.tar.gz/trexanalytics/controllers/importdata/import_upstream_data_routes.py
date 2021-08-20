'''
Created on 26 Jan 2021

@author: jacklok
'''

from flask import Blueprint, render_template, session, abort, redirect, url_for, request, jsonify
import logging, json, uuid
from flask.globals import current_app
from trexlib.utils.google.bigquery_util import create_bigquery_client, stream_data_by_datetime_partition, stream_data
from trexanalytics import conf as analytics_conf
from trexanalytics.bigquery_table_template_config import CUSTOMER_TRANSACTION_TEMPLATE, MERCHANT_REGISTERED_CUSTOMER_TEMPLATE
from trexmodel.models.datastore.analytic_models import UpstreamData
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexanalytics.controllers.importdata.import_data_base_routes import TriggerImportDataBaseResource, InitImportDataBaseResource, ImportDataBaseResource
from flask_restful import Api
from trexlib.utils.string_util import is_not_empty, random_string
from trexanalytics.bigquery_table_template_config import TABLE_SCHEME_TEMPLATE


import_upstream_data_bp = Blueprint('import_upstream_data_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/import-upstream-data')

logger = logging.getLogger('import')

import_upstream_data_api = Api(import_upstream_data_bp)

class TriggerImportAllUpstreamData(TriggerImportDataBaseResource):
    
    def get_task_url(self):
        return '/import-upstream-data/init-import-all-upstream-data'
    
    def get_task_queue(self):
        return 'import-upstream'
    
    
    
    
class InitImportAllUpstreamData(InitImportDataBaseResource):
    def get_import_data_count(self, **kwargs):
        return count_all_unsend_upstream_data()
    
    def get_import_data_page_size(self):
        return analytics_conf.STREAM_DATA_PAGE_SIZE
    
    def get_task_url(self):
        return '/import-upstream-data/import-all-upstream-data'
    
    def get_task_queue(self):
        return 'import-upstream'
    

def count_all_unsend_upstream_data():
    db_client = create_db_client(caller_info="count_all_unsend_upstream_data")
    with db_client.context():
        count       = UpstreamData.count_not_sent()
    return count


class ImportAllUpstreamData(ImportDataBaseResource): 
    def import_data(self, offset, limit, **kwargs):
        logger.debug('Going to import data now')
        logger.debug('offset=%d limit=%d', offset, limit)
        
        
        try:
            start_cursor    = kwargs.get('start_cursor')
            batch_id        = kwargs.get('batch_id')
            
            logger.debug('ImportAllUpstreamData: start_cursor=%s', start_cursor)
            logger.debug('ImportAllUpstreamData: batch_id=%s', batch_id)
            
            next_cursor     = import_all_unsend_upstream_data_function(dataset_name='system', limit=limit, start_cursor=start_cursor, batch_id=batch_id)
            
            logger.debug('ImportAllUpstreamData: next_cursor=%s', next_cursor)
            
            return next_cursor
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
    
    def get_task_url(self):
        return '/import-upstream-data/import-all-upstream-data'
    
    def get_task_queue(self):
        return 'import-upstream'
    
def import_all_unsend_upstream_data_function(credential_info=None, dataset_name='system_dataset', 
                                            limit=analytics_conf.STREAM_DATA_PAGE_SIZE, start_cursor=None, batch_id=None):
    
    
    logger.debug('credential_filepath=%s', analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    logger.debug('bg_client.project=%s', bg_client.project)
    
    if credential_info is None:
        credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="import_registered_customer_function")
    import_upstream_dict = {}
    
    logger.debug('import_all_unsend_upstream_data_function (%s): start_cursor=%s', batch_id, start_cursor)
    
    
    
    with db_client.context():
        (upstream_data_list, next_cursor) = UpstreamData.list_not_send(limit = limit, start_cursor=start_cursor, return_with_cursor=True)
    
    import_count    = len(upstream_data_list)
    errors          = []    
    imported_count  = 0
    
    for u in upstream_data_list:
        
        table_template_name = u.table_template_name
        dataset_name        = u.dataset_name
        table_name          = u.table_name
        stream_content      = u.stream_content
        
        import_upstream_dict = {'': stream_content}


    
        logger.debug('################################ batch_id= %s ############################################', batch_id)
        logger.debug(import_upstream_dict)
        logger.debug('#####################################################################################################')
        
        __errors = stream_data(bg_client, dataset_name, table_template_name, 
                                                   TABLE_SCHEME_TEMPLATE.get(table_template_name), table_name, stream_content
                                                   )
        
        if len(__errors)>0:
            errors.extend(__errors)
        else:
            with db_client.context():
                u.is_sent = True
                u.put()
                logger.debug("New rows have been added")
                
            imported_count+=1
            
    bg_client.close()
    
    if errors==[]:
        logger.debug('imported_count=%d', imported_count)
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    return next_cursor
    
@import_upstream_data_bp.route('/upstream/data-content/<upstream_data_key>')
def read_upstream_data_content(upstream_data_key):
    
    logger.debug('upstream_data_key=%s', upstream_data_key)
    
    try:
        db_client = create_db_client(caller_info="read_upstream_data_content")
        with db_client.context():
            upstream_data = UpstreamData.fetch(upstream_data_key)
            
        if upstream_data:
            return jsonify(upstream_data.stream_content)
    except:
        logger.debug('Failed to fetch upstream data due to %s', get_tracelog())
    
    return 'Not found', 200

import_upstream_data_api.add_resource(TriggerImportAllUpstreamData,   '/trigger-import-all-upstream-data')
import_upstream_data_api.add_resource(InitImportAllUpstreamData,      '/init-import-all-upstream-data')
import_upstream_data_api.add_resource(ImportAllUpstreamData,          '/import-all-upstream-data')

        