from sixgill.sixgill_base_client import SixgillBaseClient
from sixgill.sixgill_request_classes.sixgill_actionable_alerts_request import SixgillActionableAlertsGetRequest
from sixgill.sixgill_request_classes.sixgill_specific_actionable_alert_request import \
    SixgillSpecificActionableAlertGetRequest
from sixgill.sixgill_request_classes.sixgill_actionable_alert_content_request import \
    SixgillActionableAlertContentGetRequest


class SixgillActionableAlertClient(SixgillBaseClient):

    def __init__(self, client_id, client_secret, channel_id, logger=None, session=None, verify=False,
                 num_of_attempts=5):
        super(SixgillActionableAlertClient, self).__init__(client_id=client_id, client_secret=client_secret,
                                                           channel_id=channel_id, logger=logger,
                                                           session=session, verify=verify,
                                                           num_of_attempts=num_of_attempts)

    def get_actionable_alerts_bulk(self, limit=50, offset=0, sort_by=None,
                                   sort_order=None, is_read=None, threat_level=None,
                                   threat_type=None, organization_id=None):
        return self._send_request(
            SixgillActionableAlertsGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                              limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order,
                                              is_read=is_read, threat_level=threat_level, threat_type=threat_type,
                                              organization_id=organization_id))

    def get_actionable_alert(self, actionable_alert_id, organization_id=None):
        return self._send_request(
            SixgillSpecificActionableAlertGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                                     actionable_alert_id=actionable_alert_id,
                                                     organization_id=organization_id))

    def get_actionable_alert_content(self, actionable_alert_id, limit=100, highlight=False, organization_id=None):
        raw_response = self._send_request(
            SixgillActionableAlertContentGetRequest(channel_id=self.channel_id, access_token=self._get_access_token(),
                                                    actionable_alert_id=actionable_alert_id, limit=limit,
                                                    highlight=highlight, organization_id=organization_id))
        alert_content = raw_response.get('content', {"items": [], "total": 0})

        return alert_content
