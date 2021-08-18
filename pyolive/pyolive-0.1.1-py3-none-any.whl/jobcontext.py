from dataclasses import dataclass

@dataclass
class JobContext:
    regkey:str
    topic:str
    author:str
    action_id:int
    action_ns:str
    action_app:str
    action_params:str
    job_id:str
    timestamp:int
    filenames:list
    msgbox:dict

    def __init__(self, message):
        self.first = True
        self.regkey = message['regkey']
        self.topic = message['topic']
        self.author = message['author']
        self.action_id = int(message['action-id'])
        self.action_ns = message['action-ns']
        self.action_app = message['action-app']
        self.action_params = message['action-params']
        self.job_id = message['job-id']
        self.timestamp = int(message['timestamp'])
        self.filenames = message['filenames'][:]
        self.msgbox = message['msgbox']

    def set_filename(self, filename):
        if self.first:
            self.filenames = []
            self.filenames.append(filename)
            self.first = False
        else:
            self.filenames.append(filename)

