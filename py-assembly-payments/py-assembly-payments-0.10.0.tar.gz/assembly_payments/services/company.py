
from assembly_payments.services.base import BaseService
from assembly_payments.types import Company, CompanyRequest


class CompanyService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/companies"

    def get(self, company_id):
        response = self._execute(CompanyService.GET, f"{self.endpoint}/{company_id}")
        return Company(**response['companies'])

    def list(self, *args, **kwargs):
        response = self._execute(CompanyService.GET, self.endpoint)
        return list(map(lambda x: Company(**x), response.get("companies", [])))

    def create(self, **kwargs):
        data = CompanyRequest(**kwargs)
        response = self._execute(CompanyService.POST, self.endpoint, data=data.dict())
        return Company(**response['companies'])
