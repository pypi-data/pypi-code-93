from abc import ABC
import datetime

from lgt_data.mongo_repository import UserLeadMongoRepository
from pydantic import BaseModel
from ..basejobs import BaseBackgroundJob, BaseBackgroundJobData

"""
Archive user leads
"""
class ArchiveLeadsJobData(BaseBackgroundJobData, BaseModel):
    user_id: str

class ArchiveLeadsJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return ArchiveLeadsJobData

    def exec(self, data: ArchiveLeadsJobData):
        lead_repository = UserLeadMongoRepository()
        leads = lead_repository.get_leads(data.user_id, 0, 1000, archived=False,
                                          to_date=datetime.datetime.utcnow() - datetime.timedelta(days=90))

        for lead in leads:
            lead_repository.update_lead(data.user_id, lead.id, archived=True)