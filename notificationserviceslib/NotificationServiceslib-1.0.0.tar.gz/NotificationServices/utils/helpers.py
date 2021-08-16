# Mappings for easier user interaction and standard slack templates
class Mappings:

    def __init__(self):
        types = {
            "subject" : "header",
            "plain_text" : "context",
            "link" : "section"
        }
        
        template_blocks = {

            "header" : {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "",
                    "emoji": True
                }
            },

            "context" : {
                "type": "context",
                "elements": []
            },

            "element" : {
                "type": "plain_text",
                "text": "",
                "emoji": True
            },

            "section" : {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "",
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Open",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "url": "https://www.myntra.com/",
                    "action_id": "button-action"
                }
            },

            "divider" : {
                "type": "divider"
            }
        }

        flat_keys = {
            'header' : ('text', 'text'),
            'section' : ('text', 'text'),
            'sectionlink' : ('accessory', 'url')
        }

        self.types = types
        self.template_blocks = template_blocks
        self.flat_keys = flat_keys
        