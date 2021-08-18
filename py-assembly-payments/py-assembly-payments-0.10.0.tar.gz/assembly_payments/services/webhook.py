
from assembly_payments.services.base import BaseService
from assembly_payments.types import Webhook, WebhookRequest, WebhookUpdateRequest, Job


class WebhookService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/webhooks"

    def get(self, webhook_id):
        response = self._execute(WebhookService.GET, f"{self.endpoint}/{webhook_id}", url=self.beta_url)
        return Webhook(**response)

    def list(self, *args, **kwargs):
        response = self._execute(WebhookService.GET, self.endpoint, url=self.beta_url)
        return list(map(lambda x: Webhook(**x), response.get("webhooks", [])))

    def create(self, **kwargs):
        data = WebhookRequest(**kwargs)
        response = self._execute(WebhookService.POST, self.endpoint, data=data.dict(exclude_none=True), url=self.beta_url)
        return Webhook(**response)

    def update(self, webhook_id, **kwargs):
        data = WebhookUpdateRequest(**kwargs)
        response = self._execute(WebhookService.PATCH, f"{self.endpoint}/{webhook_id}", data=data.dict(exclude_none=True), url=self.beta_url)
        return Webhook(**response['webhooks'])

    def delete(self, webhook_id):
        self._execute(WebhookService.DELETE, f"{self.endpoint}/{webhook_id}", url=self.beta_url)

    def list_jobs(self, webhook_id):
        response = self._execute(WebhookService.GET, f"{self.endpoint}/{webhook_id}/jobs", url=self.beta_url)
        return list(map(lambda x: Job(**x), response.get("jobs", [])))