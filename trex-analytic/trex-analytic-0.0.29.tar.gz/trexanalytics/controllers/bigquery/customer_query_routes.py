'''
Created on 18 Jan 2021

@author: jacklok
'''
from flask import Blueprint
import logging
from trexlib.utils.google.bigquery_util import process_job_result_into_category_and_count, execute_query
from trexanalytics.controllers.bigquery.query_base_routes import CategoryAndCountQueryBaseResource,\
    QueryBaseResource
from flask_restful import Api
from trexanalytics.conf import BIGQUERY_GCLOUD_PROJECT_ID, SYSTEM_DATASET, MERCHANT_DATASET


customer_analytics_data_bp = Blueprint('customer_analytics_data_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/analytics/cust')

logger = logging.getLogger('analytics')

query_customer_data_api = Api(customer_analytics_data_bp)

@customer_analytics_data_bp.route('/index')
def query_customer_index(): 
    return 'ping', 200


class QueryAllCustomerGrowthByYearMonth(CategoryAndCountQueryBaseResource):
    def prepare_query(self, **kwrgs):
        
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        where_condition  = ''
        
        if date_range_from and date_range_to:
            where_condition = "WHERE _TABLE_SUFFIX BETWEEN '{date_range_from}' and '{date_range_to}'".format(date_range_from=date_range_from, 
                                                                                                         date_range_to=date_range_to)
        
        query = '''
            SELECT FORMAT_DATETIME('%Y-%m', RegisteredDateTime) as year_month, sum(count_by_date) as count
            FROM (
            SELECT RegisteredDateTime, count(*) as count_by_date FROM
                (
                        SELECT CustomerKey, RegisteredDateTime
                        FROM `{project_id}.{dataset_name}.registered_customer_*`
                        {where_condition}
                        GROUP BY CustomerKey, RegisteredDateTime
                ) GROUP BY RegisteredDateTime       
            ) GROUP BY year_month            
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=SYSTEM_DATASET, where_condition=where_condition)    
            
        logger.debug('execute_all_registered_customer_by_year_month: query=%s', query)
    
        return query 
    
class QueryMerchantCustomerGrowthByYearMonth(CategoryAndCountQueryBaseResource):
    def prepare_query(self, **kwrgs):
        account_code      = kwrgs.get('account_code')
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        account_code = account_code.replace('-','')
        
        where_condition  = ''
        
        if date_range_from and date_range_to:
            where_condition = "WHERE _TABLE_SUFFIX BETWEEN '{date_range_from}' and '{date_range_to}'".format(date_range_from=date_range_from, 
                                                                                                         date_range_to=date_range_to)
        
        query = '''
            SELECT FORMAT_DATETIME('%Y-%m', RegisteredDateTime) as year_month, sum(count_by_date) as count
            FROM (
            SELECT RegisteredDateTime, count(*) as count_by_date FROM
                (
                        SELECT CustomerKey, RegisteredDateTime
                        FROM `{project_id}.{dataset_name}.merchant_registered_customer_{account_code}_*`
                        {where_condition}
                        GROUP BY CustomerKey, RegisteredDateTime
                ) GROUP BY RegisteredDateTime       
            ) GROUP BY year_month            
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=MERCHANT_DATASET, where_condition=where_condition, account_code=account_code)    
            
        logger.info('execute_all_registered_customer_by_year_month: query=%s', query)
    
        return query 
    
class QueryMerchantCustomerCountByDateRange(QueryBaseResource):
    def prepare_query(self, **kwrgs):
        account_code      = kwrgs.get('account_code')
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        account_code = account_code.replace('-','')
        
        where_condition  = ''
        
        if date_range_from and date_range_to:
            where_condition = "WHERE _TABLE_SUFFIX BETWEEN '{date_range_from}' and '{date_range_to}'".format(date_range_from=date_range_from, 
                                                                                                         date_range_to=date_range_to)
        
        query = '''
            SELECT count(*) as customerCount FROM
                (
                        SELECT CustomerKey, RegisteredDateTime
                        FROM `{project_id}.{dataset_name}.merchant_registered_customer_{account_code}_*`
                        {where_condition}
                        GROUP BY CustomerKey, RegisteredDateTime
                )       
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=MERCHANT_DATASET, where_condition=where_condition, account_code=account_code)    
            
        logger.debug('QueryMerchantCustomerCountByDateRange: query=%s', query)
    
        return query 
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            column_dict['customerCount']        = row.customerCount
            
            row_list.append(column_dict)
        
        return row_list 
    
class QueryMerchantCustomerGenderByDateRange(QueryBaseResource):
    def prepare_query(self, **kwrgs):
        account_code      = kwrgs.get('account_code')
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        account_code = account_code.replace('-','')
        
        where_condition  = ''
        
        if date_range_from and date_range_to:
            where_condition = "WHERE _TABLE_SUFFIX BETWEEN '{date_range_from}' and '{date_range_to}'".format(date_range_from=date_range_from, 
                                                                                                         date_range_to=date_range_to)
        
        query = '''
            SELECT coalesce(Gender,'u') as gender, count(*) as genderCount FROM
                (
                
                SELECT
                  checking.Key, checking.CustomerKey, checking.UpdatedDateTime, checking.Gender as gender
                FROM
                  (
                  SELECT
                     CustomerKey, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                   FROM
                    `{project_id}.{dataset_name}.merchant_registered_customer_{account_code}_*`
                    {where_condition}
                    
                  GROUP BY
                 CustomerKey
                 ) 
                 AS latest_customers
            INNER JOIN 
            (
              SELECT 
              Key, CustomerKey, UpdatedDateTime, Gender
              FROM
              `{project_id}.{dataset_name}.merchant_registered_customer_{account_code}_*`
              {where_condition} 
                 
            ) as checking
            ON
              checking.CustomerKey = latest_customers.CustomerKey
              AND
              checking.UpdatedDateTime=latest_customers.latestUpdatedDateTime
            ) group by gender      
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=MERCHANT_DATASET, where_condition=where_condition, account_code=account_code)    
            
        logger.debug('QueryMerchantCustomerCountByDateRange: project_id=%s', BIGQUERY_GCLOUD_PROJECT_ID)
        logger.debug('QueryMerchantCustomerCountByDateRange: query=%s', query)
    
        return query 
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            column_dict['gender']        = row.gender
            column_dict['count']        = row.genderCount
            
            row_list.append(column_dict)
        
        return row_list 
    
class QueryMerchantCustomerAgeGroupByDateRange(QueryBaseResource):
    def prepare_query(self, **kwrgs):
        account_code      = kwrgs.get('account_code')
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        account_code = account_code.replace('-','')
        
        where_condition  = ''
        
        if date_range_from and date_range_to:
            where_condition = "WHERE _TABLE_SUFFIX BETWEEN '{date_range_from}' and '{date_range_to}'".format(date_range_from=date_range_from, 
                                                                                                         date_range_to=date_range_to)
        
        query = '''
            SELECT age_group, sum(group_count) as count  FROM (

                SELECT age_group, count(*) as group_count FROM (
                    SELECT CASE 
                       WHEN age >=  0 AND age < 20 THEN '0-19'
                       WHEN age >= 20 AND age < 30 THEN '20-29'
                       WHEN age >= 30 AND age < 40 THEN '30-39'
                       WHEN age >= 40 AND age < 50 THEN '40-49'
                       WHEN age >= 50 AND age < 60 THEN '50-59'
                       WHEN age >= 60 AND age < 70 THEN '60-69'
                       WHEN age >= 70 AND age < 80 THEN '70-79'
                       WHEN age >= 80              THEN '>=80'
                       ELSE 'unknown' END as age_group
            
                        FROM(
            
                            SELECT IFNULL(DATE_DIFF(CURRENT_DATE(),DOB, YEAR), -1) as age
                                FROM(
            
                                SELECT
                                  checking.Key, checking.CustomerKey, checking.UpdatedDateTime, checking.DOB as DOB
                                FROM
                                  (
                                  SELECT
                                     CustomerKey, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                                   FROM
                                     `{project_id}.{dataset_name}.merchant_registered_customer_{account_code}_*`
                                     {where_condition} 
            
                                   GROUP BY
                                     CustomerKey
                                     ) 
                                     AS latest_customers
                                INNER JOIN
                                (
                                  SELECT 
                                  Key, CustomerKey, UpdatedDateTime, DOB
                                  FROM
                                  `{project_id}.{dataset_name}.merchant_registered_customer_{account_code}_*`
                                  {where_condition} 
            
                                ) as checking
                                
                                ON
                                    
                                checking.CustomerKey = latest_customers.CustomerKey
                                AND
                                checking.UpdatedDateTime=latest_customers.latestUpdatedDateTime
                            ) 
                        )                 
                ) group by age_group
            ) group by age_group
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=MERCHANT_DATASET, where_condition=where_condition, account_code=account_code)    
            
        logger.debug('QueryMerchantCustomerCountByDateRange: query=%s', query)
    
        return query 
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            column_dict['age_group']    = row.age_group
            column_dict['count']        = row.count
            
            row_list.append(column_dict)
        
        return row_list                   
    

def execute_all_registered_customer_by_year_month(bg_client, project_id, dataset_name):
    
    query = '''
            SELECT FORMAT_DATETIME('%Y-%m-%d', RegisteredDateTime) as year_month, sum(count_by_date) as count
            FROM (
            SELECT RegisteredDateTime, count(*) as count_by_date
                        FROM `{project_id}.{dataset_name}.registered_customer_*`
                        GROUP BY RegisteredDateTime
            ) GROUP BY year_month            
            '''.format(project_id=project_id, dataset_name=dataset_name)
    
    logger.debug('execute_all_registered_customer_by_year_month: query=%s', query)
    
    return execute_query(bg_client, query)


def process_all_registered_customer_by_year_month(job_result_rows):
    return process_job_result_into_category_and_count(job_result_rows)

query_customer_data_api.add_resource(QueryAllCustomerGrowthByYearMonth,   '/all-cust-growth-by-year-month')
query_customer_data_api.add_resource(QueryMerchantCustomerGrowthByYearMonth,   '/merchant-cust-growth-by-year-month')
query_customer_data_api.add_resource(QueryMerchantCustomerCountByDateRange,   '/merchant-cust-count-by-date-range')
query_customer_data_api.add_resource(QueryMerchantCustomerGenderByDateRange,   '/merchant-cust-gender-by-date-range')
query_customer_data_api.add_resource(QueryMerchantCustomerAgeGroupByDateRange,   '/merchant-cust-age-group-by-date-range')
