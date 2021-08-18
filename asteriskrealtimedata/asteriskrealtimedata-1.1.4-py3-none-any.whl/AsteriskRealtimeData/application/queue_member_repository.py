from antidote import service
from AsteriskRealtimeData.infrastructure.repositories.mongo.mongo_repository import (
    MongoRespository,
)


@service(singleton=True)
class QueueMemberRepository(MongoRespository):
    __tablename__: str = "queue_members"

