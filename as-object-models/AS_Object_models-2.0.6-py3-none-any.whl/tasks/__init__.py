from .. client_utils import FirestoreClient
import json,os
from google.cloud import tasks_v2

DOWNLOAD = 'download'
UPDATE_ITEM = 'updateItem'
PROCESS_UPLOAD = 'processUpload'

def create_schedule_task(scheduleType, action, payload):
    # Create a client.
    '''
    {"type": "inventory_summary", "action": "run", "payload": {"num_periods": "12","emails":["system@analyticssupply.com","jasonbowles@analyticssupply.com"]}}
    {"type": "refresh_inventory", "action": "run", "payload": {"message": "test"}}
    '''

    message = {}
    message['type'] = scheduleType
    message['action'] = action
    message['payload'] = payload
    
    client = tasks_v2.CloudTasksClient()

    # TODO(developer): Uncomment these lines and replace with your values.
    project = os.environ.get('GOOGLE_CLOUD_PROJECT','backend-firestore-test')
    queue = 'co-app-schedule'
    location = os.environ.get('APP_REGION','us-east4')

    # Construct the fully qualified queue name.
    parent = client.queue_path(project, location, queue)

    # Construct the request body.
    task = {
            'app_engine_http_request': {  # Specify the type of request.
                'http_method': tasks_v2.HttpMethod.POST,
                'relative_uri': '/tasks/v1/handler'
            }
    }
    if message is not None:
        # The API expects a payload of type bytes.
        converted_payload = json.dumps(message).encode()
        print(f"converted payload: {converted_payload}")

        # Add the payload to the request.
        task['app_engine_http_request']['body'] = converted_payload

    # Use the client to build and send the task.
    response = client.create_task(parent=parent, task=task)

    print('Created task {}'.format(response.name))
    return response


def send_task(queue_name, handler, payload, svc_acct_email, useFunction=False):
    '''
    Expectation is that the payload will be a dict... we'll dump that to json, then encode
    '''
    clt = FirestoreClient.getInstance()
    task = {}
    
    if useFunction:
        task['http_request'] = {
            'url': handler,
            'oidc_token': {
               'service_account_email': svc_acct_email,
            },
           'headers': {
               'Content-Type': 'application/json',
           }
        }
        if payload is not None:
            converted_payload = payload.encode()
            task['http_request']['body'] = converted_payload
            task['http_request']['http_method'] = 'POST'
        else:
            task['http_request']['http_method'] = 'GET'
    else:
        task['app_engine_http_request'] = {
            'relative_uri': handler,
            'oidc_token': {
               'service_account_email': svc_acct_email,
            }
        }
        if payload is not None:
            converted_payload = payload.encode()
            task['app_engine_http_request']['body'] = converted_payload
            task['app_engine_http_request']['http_method'] = 'POST'
        else:
            task['app_engine_http_request']['http_method'] = 'GET'


    path = clt.task_queues.get(queue_name,None)
    if path is None:
        raise Exception("Invalid Queue Name")

    response = clt.tasksClient.create_task(path, task)
    print('Created task {}'.format(response.name))
    return response