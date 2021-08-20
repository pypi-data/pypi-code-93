'''
Created on 11 Jan 2021

@author: jacklok
'''

from flask import Blueprint, render_template, session, abort, redirect, url_for, jsonify
import logging, json
from flask.globals import current_app
from flask.json import jsonify
from json import JSONEncoder
from datetime import datetime, date
from trexanalytics import conf as analytics_conf
from google.oauth2 import service_account 
from google.cloud import bigquery

main_bp = Blueprint('main_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/')

logger = logging.getLogger('debug')

class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()


def create_bigquery_client(info=None, credential_filepath=None):
    if info:
        cred = service_account.Credentials.from_service_account_info(info)
        
    else:
        if credential_filepath:
            cred = service_account.Credentials.from_service_account_file(credential_filepath)
        else:
            cred = service_account.Credentials.from_service_account_file(
                                                            analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH)

    client = bigquery.Client(project=analytics_conf.GCLOUD_PROJECT_ID, credentials=cred)
    
    return client        

@main_bp.route('/')
def home_page(): 
    
    return 'Welcome to %s project' % analytics_conf.APPLICATION_NAME, 200
    
@main_bp.route('/config')
def app_config():     
    config_dict = {}
    config_dict.update(current_app.config)
    config_dict['BIGQUERY_SERVICE_CREDENTIAL_PATH'] = analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH
    
    config_json_str = json.dumps(config_dict, indent=4, cls=DateTimeEncoder)
    #return jsonify(json.dumps(config_dict, indent=4, cls=DateTimeEncoder))
    
    response = current_app.response_class(
        response=config_json_str,
        status=200,
        mimetype='application/json'
    )
    return response

@main_bp.route('/ping')
def ping():
    return 'ping', 200

@main_bp.route('/test')
def test():
    bigquery_client = create_bigquery_client()
    
    logger.debug('bigquery_client=%s', bigquery_client)
    
    return 'Test', 200


