from antidote import service
from AsteriskRealtimeData.infrastructure.repositories.mongo.mongo_repository import (
    MongoRespository,
)


@service(singleton=True)
class QueueStatusRepository(MongoRespository):
    __tablename__: str = "queues_status"
