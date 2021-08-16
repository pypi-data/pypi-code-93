import logging

from . import Client, HttpAuth

logger = logging.getLogger(__name__)


class ReportingClient(Client):
    """API Client for the Reporting Service."""
    def __init__(self, endpoint, token):
        super().__init__()
        self.ENDPOINT = endpoint.rstrip('/')
        self.token = token

    @property
    def auth(self):
        """The Reporting Service uses Digest Authentication."""
        return HttpAuth(self.token, key='X-RBX-TOKEN')

    def create_schedule(self, body, campaign, cron, format, name, recipients, reports):
        """Create a scheduled job.

        Return the job_id of the job just created.
        """
        response = self._post('/schedule', data={
            'body': body,
            'campaign': campaign,
            'cron': cron,
            'format': format,
            'name': name,
            'recipients': recipients,
            'reports': reports,
        })
        return response.get('job_id')

    def delete_schedule(self, job_id):
        """Create the scheduled job."""
        response = self._post('/schedule/delete', data={'job_id': job_id})
        return response.get('job_id')

    def pause_schedule(self, job_id):
        """Pause the scheduled job."""
        response = self._post('/schedule/pause', data={'job_id': job_id})
        return response.get('job_id')

    def resume_schedule(self, job_id):
        """Resume the scheduled job."""
        response = self._post('/schedule/resume', data={'job_id': job_id})
        return response.get('job_id')

    def update_schedule(self, body, campaign, cron, format, job_id, name, recipients, reports):
        """Update the scheduled job."""
        response = self._post('/schedule', data={
            'body': body,
            'campaign': campaign,
            'cron': cron,
            'format': format,
            'job_id': job_id,
            'name': name,
            'recipients': recipients,
            'reports': reports,
        })
        return response.get('job_id')
