'''
Created on 18 Sep 2020

@author: jacklok
'''
import logging, os, config_path

APPLICATION_NAME                                    = 'Trex Analytics'
APPLICATION_TITLE                                   = 'Trex Analytics Platform'
APPLICATION_DESC                                    = 'Trex Analytics is used to anlayze data project'
APPLICATION_HREF                                    = 'http://localhost.com:8084/'

PRODUCTION_MODE                                     = "PROD"
DEMO_MODE                                           = "DEMO"
LOCAL_MODE                                          = "LOCAL"


#DEPLOYMENT_MODE                                     = PRODUCTION_MODE
DEPLOYMENT_MODE                                     = DEMO_MODE
#DEPLOYMENT_MODE                                     = LOCAL_MODE

#DEPLOYMENT_MODE                                     = PRODUCTION_MODE
#DEPLOYMENT_MODE                                     = DEMO_MODE
DEPLOYMENT_MODE                                     = LOCAL_MODE


CSRF_ENABLED                                        = True

CONTENT_WITH_JAVASCRIPT_LINK                        = True
 
APPLICATION_VERSION_NO                              = "25092020"

DEFAULT_LANGUAGE                                    = 'en_us'

GCLOUD_PROJECT_ID                                   = os.environ.get('GCLOUD_PROJECT_ID')
#ANALYTICS_GCLOUD_PROJECT_ID                         = os.environ.get('ANALYTICS_GCLOUD_PROJECT_ID')
#ANALYTICS_GCLOUD_LOCATION                           = os.environ.get('ANALYTICS_GCLOUD_LOCATION')

SUPERUSER_ID                                        = os.environ.get('SUPERUSER_ID')
SUPERUSER_EMAIL                                     = os.environ.get('SUPERUSER_EMAIL')
SUPERUSER_HASHED_PASSWORD                           = os.environ.get('SUPERUSER_HASHED_PASSWORD')

#SERVICE_ACCOUNT_KEY_FILEPATH                        = os.environ['SERVICE_ACCOUNT_KEY']
#SERVICE_CREDENTIAL_PATH                             = os.path.abspath(os.path.dirname(__file__)) + '/../' + SERVICE_ACCOUNT_KEY_FILEPATH

#ANALYTICS_SERVICE_ACCOUNT_KEY_FILEPATH              = os.environ['ANALYTICS_SERVICE_ACCOUNT_KEY']
#ANALYTICS_SERVICE_CREDENTIAL_PATH                   = os.path.abspath(os.path.dirname(__file__)) + '/../' + ANALYTICS_SERVICE_ACCOUNT_KEY_FILEPATH

BIGQUERY_GCLOUD_PROJECT_ID                          = os.environ.get('BIGQUERY_GCLOUD_PROJECT_ID')
BIGQUERY_SERVICE_ACCOUNT_KEY_FILEPATH               = os.environ['BIGQUERY_SERVICE_ACCOUNT_KEY']
BIGQUERY_SERVICE_CREDENTIAL_PATH                    = os.path.abspath(os.path.dirname(config_path.__file__)) +'/'+ BIGQUERY_SERVICE_ACCOUNT_KEY_FILEPATH
BIGQUERY_GCLOUD_LOCATION                            = os.environ.get('BIGQUERY_GCLOUD_LOCATION')

ANALYTICS_BASE_URL                                  = os.environ.get('ANALYTICS_BASE_URL')
UPSTREAM_BASE_URL                                   = os.environ.get('UPSTREAM_BASE_URL')
#BASE_URL                                            = 'http://a66fac3caa6b.ngrok.io'

STREAM_DATA_PAGE_SIZE                               = 100

SYSTEM_DATASET                                      = os.environ.get('SYSTEM_DATASET')
MERCHANT_DATASET                                    = os.environ.get('MERCHANT_DATASET')

ANALYTICS_TASK_GCLOUD_PROJECT_ID                    = os.environ.get('ANALYTICS_TASK_GCLOUD_PROJECT_ID')
ANALYTICS_TASK_GCLOUD_LOCATION                      = os.environ.get('ANALYTICS_TASK_GCLOUD_LOCATION')
ANALYTICS_TASK_SERVICE_ACCOUNT_KEY_FILEPATH         = os.environ.get('ANALYTICS_TASK_SERVICE_ACCOUNT_KEY')
ANALYTICS_TASK_SERVICE_CREDENTIAL_PATH              = os.path.abspath(os.path.dirname(config_path.__file__)) + '/' + ANALYTICS_TASK_SERVICE_ACCOUNT_KEY_FILEPATH
ANALYTICS_TASK_SERVICE_ACCOUNT_EMAIL                = os.environ.get('ANALYTICS_TASK_SERVICE_ACCOUNT_EMAIL')

SERVER_DATETIME_GMT                                 = os.environ.get('SERVER_DATETIME_GMT')


UPSTREAM_UPDATED_DATETIME_FIELD_NAME                = 'UpdatedDateTime'

if DEPLOYMENT_MODE==PRODUCTION_MODE:
    DEBUG_MODE       = False
    #DEBUG_MODE       = True

    #LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.WARN
    LOGGING_LEVEL    = logging.INFO
    #LOGGING_LEVEL    = logging.ERROR
    
    
    
elif DEPLOYMENT_MODE==DEMO_MODE:
    DEBUG_MODE       = True
    #DEBUG_MODE       = False
    
    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.INFO
    
    

elif DEPLOYMENT_MODE==LOCAL_MODE:
    DEBUG_MODE       = True

    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.INFO
    


