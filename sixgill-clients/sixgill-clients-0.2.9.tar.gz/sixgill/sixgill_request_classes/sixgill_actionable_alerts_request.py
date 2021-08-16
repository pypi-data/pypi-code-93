from sixgill.sixgill_request_classes.sixgill_base_post_auth_request import SixgillBasePostAuthRequest


class SixgillActionableAlertsGetRequest(SixgillBasePostAuthRequest):
    end_point = 'alerts/actionable-alert'
    method = 'GET'

    def __init__(self, channel_id, access_token, limit, offset, sort_by,
                 sort_order, is_read, threat_level, threat_type, organization_id):
        super(SixgillActionableAlertsGetRequest, self).__init__(channel_id, access_token)

        self.request.params['fetch_size'] = limit
        self.request.params['offset'] = offset
        self.request.params['sort_by'] = sort_by
        self.request.params['sort_order'] = sort_order
        self.request.params['is_read'] = is_read
        self.request.params['threat_level'] = threat_level
        self.request.params['threat_type'] = threat_type
        if organization_id:
            self.request.params['organization_id'] = organization_id
