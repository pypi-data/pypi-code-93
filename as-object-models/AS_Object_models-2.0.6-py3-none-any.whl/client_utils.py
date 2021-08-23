from flask import request

from google.cloud import firestore
from google.cloud import storage
from google.cloud import tasks_v2
from google.cloud import pubsub

import logging,os

class FirestoreClient:

    _instances = {}

    def __init__(self, user_email,project_name=None):
        self.user_email = user_email
        if project_name is None:
            project_name = os.environ.get('GOOGLE_CLOUD_PROJECT',None)
            
        self.project = project_name
        self.fsClient = firestore.Client() if project_name is None else firestore.Client(project=project_name)
        self.storeClient = storage.Client() if project_name is None else storage.Client(project=project_name)
        self.tasksClient = tasks_v2.CloudTasksClient()
        self.pubsubClient = pubsub.PublisherClient()
        self.task_queues = {}
        self._create_q_paths(project_name)
        self.pubsub_topics = {}
        self._create_pubsub_topics(project_name)
        self.storage_bucket = os.environ.get("STORE_BUCKET",'backend-firestore-test.appspot.com')
        self.company = os.environ.get('APP_FIRESTORE_COMPANY',None)
        self.application = os.environ.get('APP_FIRESTORE_NAME',None)
        if not self.company or not self.application:
            raise Exception("The company name and application name must be set in environment variables ('APP_FIRESTORE_COMPANY','APP_FIRESTORE_NAME'")

    def _create_q_paths(self, project_name):
        project = project_name
        location = 'us-east4'
        self.task_queues = {x:self.tasksClient.queue_path(project,location,x) for x in ['download','processUpload','updateItem','co-app-schedule']}

    def _create_pubsub_topics(self, project_name):
        self.pubsub_topics = {x:f'projects/{project_name}/topics/{x}' for x in ['download','processUpload','updateItem','updateMonthInventory','refreshItemList','co-apps-schedule']}

    @classmethod
    def getInstance(cls,inEmail=None,project_name=None):
        key = 'system'
        client = FirestoreClient._instances.get(key,SystemClient(project_name))
        if inEmail:
            key = 'api_'+str(inEmail)
            client = FirestoreClient._instances.get(key,ApiUserClient(inEmail,project_name))

        email = None
        if request:
            email = request.headers.get('X-Goog-Authenticated-User-Email',None)
            
        if email:
            key = 'user_'+email
            client = FirestoreClient._instances.get(key,UserClient(project_name))
    
        FirestoreClient._instances[key] = client
        return client

class CustomClient(FirestoreClient):

    def __init__(self,project_name=None):
        super(SystemClient,self).__init__('system@analyticssupply.com',project_name)
        
class SystemClient(FirestoreClient):

    def __init__(self,project_name=None):
        super(SystemClient,self).__init__('system@analyticssupply.com',project_name)

class UserClient(FirestoreClient):

    def __init__(self,project_name=None):
        user_email = request.headers.get('X-Goog-Authenticated-User-Email','none:system@analyticssupply.com').split(":")[1]
        super(UserClient,self).__init__(user_email,project_name)

class ApiUserClient(FirestoreClient):

    def __init__(self,email,project_name=None):
        super(ApiUserClient,self).__init__(email,project_name)
