from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.source import SourceRecord
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result

from tracardi_mongodb_connector.model.client import MongoClient
from tracardi_mongodb_connector.model.configuration import PluginConfiguration, MongoConfiguration


class MongoConnectorAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'MongoConnectorAction':
        plugin = MongoConnectorAction(**kwargs)
        source_config_record = await Entity(id=plugin.config.source.id). \
            storage('source'). \
            load(SourceRecord)  # type: SourceRecord

        if source_config_record is None:
            raise ValueError('Source id {} for mongo plugin does not exist.'.format(plugin.config.source.id))

        source_config = source_config_record.decode()

        mongo_config = MongoConfiguration(
            **source_config.config
        )

        plugin.client = MongoClient(mongo_config)

        return plugin

    def __init__(self, **kwargs):
        self.config = PluginConfiguration(**kwargs)
        self.client = None  # type: Optional[MongoClient]

    async def run(self, query):
        result = self.client.find(self.config.mongo.database, self.config.mongo.collection, query)
        return Result(port="payload", value=list(result))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi_mongodb_connector.plugin',
            className='MongoConnectorAction',
            inputs=["query"],
            outputs=['payload'],
            version='0.1.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "source": {
                    "id": None,
                },
                "mongo": {
                    "database": None,
                    "collection": None
                }
            }

        ),
        metadata=MetaData(
            name='Mongo connector',
            desc='Connects to mongodb and reads data.',
            type='flowNode',
            width=200,
            height=100,
            icon='mongo',
            group=["Connectors"]
        )
    )
