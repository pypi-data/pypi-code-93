from NotificationServices.notifier.controller import NotificationController
import requests
import json
from NotificationServices.utils import exceptions
from flatten_dict import flatten
from flatten_dict import unflatten
from NotificationServices.utils import helpers
from NotificationServices.providers.get_config import configuration

class Slack(NotificationController):

    def __init__(self, config = None):
        
        contents = [
        {
            'message' : 'Test',
            'type' : 'subject',
        },
        {
            'message' : 'Test',
            'type' : 'plain_text',
        },
        {
            'message' : 'test_link',
            'type' : 'link',
            'url' : 'https://www.myntra.com/',
        },
        ]
        self.requirement = {
            "required": ["provider_name : slack", "slack_url : str", "contents : dict"],#----> changes made added provide_name entry
            "contents": json.dumps(contents)
        }
        
        if config:
            f = open(config)
            config = json.load(f)
            slack_config = config['slack']
            f.close()
        else:
            f = configuration()
            slack_config = f['slack']

        self.slack_url = slack_config['slack_url']
        self.header = slack_config['header']

    def required(self) -> dict:
        return self.requirement

    def _validate_data(self, **data):
       
        for block in data['contents']:
            block_keys = block.keys()
            required_keys = ["message", "type"]
            for key in required_keys:
                if key not in block_keys:
                    return False
        return True 

    def _process_data(self, **data):
        if self._validate_data(**data):
            return self._build_data(data)
        else:
            raise exceptions.InvalidInput

    def _build_data(self, data) -> None:

        if "slack_url" in data.keys():
            self.slack_url = data["slack_url"]
        contents = data['contents']
        maps = helpers.Mappings()
        template_blocks = maps.template_blocks
        types = maps.types
        flat_keys = maps.flat_keys
        
        self.slackpost = {
            "blocks" : []
        }

        # Loop over the input content and create a blocks corresponding to their type
        for content in contents:
            message = content['message']
            block_type = types[content['type']]
            if block_type == "section":
                if 'url' in content:
                    link = content['url']
                else:
                    link = "<Placeholder>"
            
            # Getting the template block for the current type (header/context/section)
            block = template_blocks[block_type]

            '''
            Logic to replace the blank text/ url with desired text/ url
            1) Flatten the dictionary
            2) Look for the required key in the flattened dictionaries using predefined keys for every type pf block
            3) Replace the value corresponding to this key
            4) Unflatten the dictionary
            '''

            # Handling for the problem where elements is an array
            if block_type == "context":
                temp_block = template_blocks['element']
                temp_block['text'] = message
                block['elements'].append(temp_block)

            # Handling for extra url field in case of section block
            elif block_type == "section":
                block = flatten(block)
                block[flat_keys[block_type]] = message
                block[flat_keys[f"{block_type}link"]] = link
                block = unflatten(block)

            else:
                block = flatten(block)
                block[flat_keys[block_type]] = message
                block = unflatten(block)

            self.slackpost['blocks'].append(block)
            self.slackpost['blocks'].append(template_blocks['divider'])

        return self.slackpost

    def slack_notification(self):

        # Curl request to slack and status report
        try:
            response = requests.request('POST', self.slack_url, data=json.dumps(self.slackpost), headers = self.header, timeout=3)
            if response.status_code == 200:
                # Getting channel_id from slack_url
                channel_id = self.slack_url.split('/')
                return json.dumps({
                    'statusCode' : 200,
                    'statusMessage' : f"Message sent successfully to slack channel: {channel_id[5]}",
                    'statusType' : 'SUCCESS',
                    'response' : {
                        "provider" : "slack",
                        "report" : response.text
                    }
                }, indent=4)

        except requests.ConnectTimeout:
            response = ""
            raise exceptions.SlackExceptions(self.slack_url, response, connect_timeout = True)
        
        raise exceptions.SlackExceptions(self.slack_url, response)

    def _send_notification(self):
        try:
            res = self.slack_notification()
            return res
        except exceptions.SlackExceptions as e:
            raise e