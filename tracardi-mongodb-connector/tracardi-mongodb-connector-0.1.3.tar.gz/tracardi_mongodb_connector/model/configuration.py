from pydantic import BaseModel
from tracardi.domain.entity import Entity


class MongoConfiguration(BaseModel):
    uri: str
    timeout: int = 5000


class MongoResource(BaseModel):
    database: str = None
    collection: str = None


class PluginConfiguration(BaseModel):
    source: Entity
    mongo: MongoResource
