import json

# Custom exceptions for email
class EmailExceptions(Exception):

    def __init__(self, uidx, endpoint, response, connect_timeout = False):
        self.response = response
        self.uidx = uidx
        self.endpoint = endpoint
        self.connect_timeout = connect_timeout
        super().__init__(self.response)
    
    def __str__(self):

        if self.connect_timeout:
            report = {
                'statusCode': 408,
                'statusMessage' : f"Message sent successfully to uidx {self.uidx}",
                'statusType' : "ERROR",
                'response' : ["channel : slack", "errorMeassage : Connection timed out"]
            }
            return json.dumps(report, indent = 4)

        report = {
            'statusCode' : self.response.status_code,
            'statusMessage' : f"Unable to send message to uidx: {self.uidx}",
            'statusType' : "ERROR",
            'response' : ["channel = slack"]
        }

        return json.dumps(report, indent=4)


# Custom exceptions for slack
class SlackExceptions(Exception):
    
    def __init__(self, slack_url, response, connect_timeout = False):
        self.slack_url = slack_url
        self.response = response
        self.connect_timeout = connect_timeout
        super().__init__(self.response)
    
    def __str__(self):

        # Getting channel_id from slack_url
        channel_id = self.slack_url.split('/')
        if self.connect_timeout:
            report = {
                'statusCode' : self.status_code,
                'statusMessage' : f"Unable to send message to slack channel: {channel_id[5]}",
                'statusType' : "ERROR",
                'response' : ["channel = slack"]
                
            }
            return json.dumps(report, indent=4)

        
        status_code = self.response.status_code
        report = str(self.response.text)

        # Failure
        report = {
            'statusCode' : status_code,
            'statusMessage' :f"Unable to send message to slack channel: {channel_id[5]}",
            'statusType' : "ERROR",
            'response' : ["channel = slack"]
        }

        return json.dumps(report, indent = 4)


class InvalidInput(Exception):
    def __str__(self) -> str:
        return f" Invalid Input for Slack: Use -> from notifier.controller import get_notifier \n" \
               f"then Slack = get_notifier('slack') and check the requirements using Slack.required()"
        # temp1 = {'message': 'your message', 'type' : 'select one from (\'subject\', \'plain_text\', \'link\')',
        #              'link': "Enter the 'url'"}
        # return f"Invalid Input for slack: Ensure the parameters passed 'provider_name'='slack', 'slack_url'= 'channel url' and \n 'contents' " \
        #        f"should be a list of dictionaries (i.e content = [temp1, temp2,...]) for e.g. \n temp1 = {temp1}. \n" \
        #        f"Note: the 'key's' 'message' and 'type' are must, while enter 'link' only when ('type' : 'link')  in every dictionary present in 'contents'." \
        #        f" \n call notify('provider_name'='slack', 'slack_url'='url', contents = content) to post notification on slack channel."

class InvalidInputemail(Exception):
    def __str__(self) -> str:
        return f" Invalid Input for email: Use -> from notifier.controller import get_notifier \n" \
               f"then Email = get_notifier('email') and check the requirements using Email.required()"
        # data = {
        #     'uidx' : 'having valid uidx',
        #     'subject' : 'Your subject',
        #     'html_body' : '<h1> hello! </h1>',
        #     'endpoint' : 'endpoint url',
        #     'template_name' : 'your template name',
        # }
        # return f"Invalid Input for Email: Ensure the parameters 'provider_name'='email' and data passed should be a dictionary object containing all keys" \
        #        f" with valid format \n, e.g data = {data}. \n" \
        #        f"call notify('provider_name' = 'email', **data) to post notification on email."

# {
#   "statusCode": 1001,
#   "statusMessage": "Data successfully processed",
#   "statusType": "SUCCESS",
#   "seasons": [
#     "Summer-2020",
#     "Spring-2021",
#     "Summer-2021",
#     "Spring-2019",
#     "Fall-2021"
#   ]
# }


# --------
# Error response :
# {
#     "statusCode": 400,
#     "statusType": "ERROR",
#     "statusMessage": "access_token is invalid"
# } 