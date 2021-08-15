import os
import datetime
import requests


class RescueAPI:

    def __init__(self, ):
        self.API_KEY = os.environ['RESCUETIME_API_KEY']
        self.payload = {"key": self.API_KEY}

    def endpoint(self, endpoint):
        base_url = "https://www.rescuetime.com/anapi"
        endpoint = base_url + endpoint
        return endpoint

    def get_analytic_data(self, format="json"):
        _endpoint = self.endpoint("/data")
        payload = self.payload
        payload['format'] = format
        r = requests.get(_endpoint, params=payload)
        if format.lower() == "json":
            return {'status_code': r.status_code, 'format': format,
                    'data': r.json()}
        if format.lower() == "csv":
            raise NotImplementedError

    def get_daily_summary_feed(self,):
        _endpoint = self.endpoint("/daily_summary_feed")
        payload = self.payload
        r = requests.get(_endpoint, params=payload)
        return {'status_code': r.status_code, 'json': r.json()}

    def alert_status(self, alert_id=None):
        _endpoint = self.endpoint("/alerts_feed")
        payload = self.payload
        payload['op'] = 'status'
        payload['alert_id'] = alert_id
        r = requests.get(_endpoint, params=payload)
        return {'status_code': r.status_code, 'json': r.json()}

    def list_alerts(self,):
        _endpoint = self.endpoint("/alerts_feed")
        payload = self.payload
        payload['op'] = 'list'
        r = requests.get(_endpoint, params=payload)
        return {'status_code': r.status_code, 'json': r.json()}

    def read_highlights(self, start_date=None, end_date=None):
        _endpoint = self.endpoint("/highlights_feed")
        payload = self.payload
        if start_date:
            payload['start_date'] = start_date
        if end_date:
            payload['end_date'] = end_date
        r = requests.get(_endpoint, params=payload)
        return {'status_code': r.status_code, 'json': r.json()}

    def post_highlight(self, message, highlight_date=None, source=None):
        _endpoint = self.endpoint("/highlights_post")
        now = datetime.date.today()
        payload = self.payload
        payload['highlight_date'] = highlight_date if highlight_date else now
        payload['description'] = message
        if source:
            payload['source'] = source
        r = requests.post(_endpoint, params=payload)
        return {'status_code': r.status_code, 'json': r.json()}
