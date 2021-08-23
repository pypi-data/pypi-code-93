from .. client_utils import FirestoreClient

DOWNLOAD = 'download'
UPDATE_ITEM = 'updateItem'
PROCESS_UPLOAD = 'processUpload'
UPDATE_MONTH_INVENTORY = 'updateMonthInventory'
REFRESH_ITEM_LIST = 'refreshItemList'
CO_APPS_SCHEDULE = 'co-apps-schedule'

def publish_message(topic_name, body, attributes):
    clt = FirestoreClient.getInstance()
    topic = clt.pubsub_topics.get(topic_name, None)
    if topic is not None:
        if body is None:
            body = ''
        converted_body = body.encode("utf-8")

        clt.pubsubClient.publish(topic,converted_body,**attributes)
    else:
        raise Exception("The topic doesn't exist: "+topic_name)

def publish_item_refresh():
    publish_message(REFRESH_ITEM_LIST,"Daily List Refresh",{})
