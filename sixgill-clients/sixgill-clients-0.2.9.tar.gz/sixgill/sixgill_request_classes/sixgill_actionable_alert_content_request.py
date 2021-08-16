from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillActionableAlertContentGetRequest(SixgillBasePostAuthRequest):
    end_point = None
    method = 'GET'

    def __init__(self, channel_id, access_token, actionable_alert_id, limit, highlight, organization_id):
        super(SixgillActionableAlertContentGetRequest, self).__init__(channel_id, access_token)

        self.end_point = 'alerts/actionable_alert_content/{}'.format(actionable_alert_id)
        self.request.params['limit'] = limit
        self.request.params['highlight'] = highlight
        if organization_id:
            self.request.params['organization_id'] = organization_id
