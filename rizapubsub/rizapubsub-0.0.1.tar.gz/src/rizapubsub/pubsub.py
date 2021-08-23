from bson import json_util as json
from google.auth import jwt
from google.cloud import pubsub_v1
from pydantic import BaseModel


class TaskData(BaseModel):
    topic: str
    namespace: str
    subname: str
    delay: int
    data: dict


class PubSub:
    def __init__(self, c):
        self.config = c

    def pub(self):
        audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
        credentials = jwt.Credentials.from_service_account_info(
            self.config, audience=audience)
        publisher = pubsub_v1.PublisherClient(credentials=credentials)
        return publisher

    def sub(self):
        audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"
        credentials = jwt.Credentials.from_service_account_info(
            self.config, audience=audience)
        subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
        return subscriber

    def create_topic(self, name):
        px = self.pub()
        topic_path = px.topic_path(self.config["project_id"], name)
        try:
            px.create_topic(topic_path)
            return True
        except Exception:
            return False

    def create_subscription(self, topicname, name):
        ps = self.sub()
        subscription_path = ps.subscription_path(self.config["project_id"],
                                                 name)
        try:
            ps.create_subscription(subscription_path, topicname)
            return True
        except Exception:
            return False

    def send(self, publisher, data: TaskData) -> str:
        project_id = self.config['project_id']

        msg = json.dumps(data['data']).encode("utf-8")
        topic_path = publisher.topic_path(project_id, data.get('topic'))

        future = publisher.publish(topic_path,
                                   data=msg,
                                   delay=str(data.get('delay')),
                                   subname=data.get('subname'),
                                   namespace=data.get('namespace'))

        pubsub_id = future.result()
        return pubsub_id
