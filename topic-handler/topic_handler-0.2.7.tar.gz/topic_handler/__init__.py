
from .Global import RequestFormat, ResponseError
from kafka import KafkaProducer
import re
from cryptography.hazmat.primitives.serialization.base import (
    load_pem_public_key,
)
import jwt
from random import randrange

class Aux:
    required_permissions = []
    def set_data():
        pass
    def initi_data():
        pass
    def send_response():
        pass
    
def names_to_snake_case(data):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', data.__class__.__name__).lower()


class Messages:
    def __init__(self, topic, value, offset, partition):
        self.topic = topic
        self.value = value
        self.offset = offset
        self.partition = partition


class Event:
    def __init__(self, message: Messages):
        self.message = message


class RequestData:
    auth_id: str
    response_topic: str

    def __init__(self, auth_id, response_topic):
        self.auth_id = auth_id
        self.response_topic = response_topic
class DecodeToken():
    uid:str
    aud:list[str]
    iat:int
    exp:int
    role:str
    
    def  __init__(self,token_decode:dict):
        for k, v in token_decode.items():
            setattr(self, k, v)    

class HandlerTopics():
    is_error_handler = False
    decode_token:DecodeToken

    def __init__(self, topic_list: list,table_list:list, host_kafka, pulic_key_jwt):
        self.exist_tables = list(map(lambda x: x(), table_list))
        self.exist_topics = list(map(lambda x: x(), topic_list))
        self.topics_names = list(map(names_to_snake_case, self.exist_topics))
        self.tables_names = list(map(names_to_snake_case, self.exist_tables))
        self.HOST_KAFKA = host_kafka
        self.PUBLIC_KEY_JWT = pulic_key_jwt
        self.is_error = False

    def get_instances_topics(self):
        return self.topics_names
    
    def get_instances_table(self):
        return self.tables_names

    def get_instances(self):
        return 0

    def select_topic(self, topic):
        total_topics = self.exist_topics+self.exist_tables
        self.topic = topic
        select: list[Aux] = list(
            filter(lambda x: names_to_snake_case(x) == topic,total_topics))
        if select.__len__() == 0 or select.__len__() > 1:
            self.is_error_handler = True
            return
        self.selected_topic = select[0]

    def response(self, event: Event):
        self.create_response_topic(event.message)
        if self.is_error_handler:
            self.is_error_handler =False
            return
        try:
            validate_table: list[Aux] = list(
            filter(lambda x: names_to_snake_case(x) == self.topic,self.exist_tables))
            if validate_table.__len__() == 1:
                self.selected_topic.set_data(event.message.value)
            else:
                data = RequestFormat().FromString(event.message.value)
                self.token = data.token
                self.selected_topic.initi_data(
                    data.language, data.token, self.response_topic, event.message.value)
        except:
            self.response_on_error(ResponseError(
                res=400, msg="bad request").SerializeToString())
            return
        if self.selected_topic.required_permissions:
            self.decode_jwt(self.selected_topic.required_permissions)
        if self.is_error_handler:
            self.response_on_error(ResponseError(
                res=400, msg=self.msg).SerializeToString())
            self.is_error_handler =False
            return
        self.selected_topic.send_response(self.decode_token if self.selected_topic.required_permissions else {})
        self.is_error = False
        

    def create_response_topic(self, message: Messages):
        self.response_topic = (
            message.topic
            + "_"
            + str(message.offset)
            + "_"
            + str(message.partition)
        )

    def response_on_error(self, response_model: bytes):
        producer = KafkaProducer(bootstrap_servers=self.HOST_KAFKA)
        producer.send(self.response_topic, response_model)
        producer.flush(timeout=10)

    def decode_jwt(self, required_permissions):
        pub_rsakey = load_pem_public_key(self.PUBLIC_KEY_JWT)
        try:
            options = {"require": ["uid", "aud", "iat"]}
            payload = jwt.decode(
                self.token,
                pub_rsakey,
                audience=required_permissions,
                algorithms=["RS256"],
                options=options,
            )
            self.decode_token =DecodeToken(payload)
        except jwt.ExpiredSignatureError:
            self.is_error_handler = True
            self.msg = "EXPIRED_TOKEN"
        except jwt.InvalidAudience:
            self.is_error_handler = True
            self.msg = "NOT_AUTHORIZED"
        except Exception as e:
            self.is_error_handler = True
            self.msg = str(e)

    def __hash__(self):       
        return hash(randrange(1000))
    
