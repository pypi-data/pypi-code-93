'''
Created on 11 Jan 2021

@author: jacklok
'''

from flask import Blueprint, render_template, session, abort, redirect, url_for
import logging, json
from flask.globals import current_app
from flask.json import jsonify
from json import JSONEncoder
from datetime import datetime, date
from trexlib.utils.google.bigquery_util import create_table_from_template
from trexanalytics import conf as analytics_conf

table_template_bp = Blueprint('table_template_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/template')

logger = logging.getLogger('debug')

@table_template_bp.route('/create/dataset/<dataset_name>/table-template/<table_name>')
def create_from_table_template(dataset_name, table_name): 
    created_table = create_table_from_template(dataset_name, table_name)
    
    return str(created_table), 200
