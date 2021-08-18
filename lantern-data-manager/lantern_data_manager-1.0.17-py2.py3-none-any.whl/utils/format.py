from lantern_data_manager.utils.event import get_token_attributes

def changeFormat(response):
    for element in response:
        if 'Attributes' in element:
            for attribute in element['Attributes']:
                key = attribute.pop('Name')
                value = attribute.pop('Value')
                element[key] = value
            element.pop('Attributes')

def getTeamView(event):
    token = get_token_attributes(event, ["custom:view_team"])
    if event['body']:
        event["body"]["view_team"] = token.pop("custom:view_team")
    else:
        event["view_team"] = token.pop("custom:view_team")
    return event