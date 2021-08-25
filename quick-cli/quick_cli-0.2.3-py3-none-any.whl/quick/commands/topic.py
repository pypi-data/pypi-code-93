from argparse import ArgumentParser

import isodate

from quick_client import ApiException
from quick_client import GatewaySchema
from quick_client.models import QuickTopicType
from quick_client.models import TopicCreationData
from quick_client.models import TopicWriteType

from quick.commands.base import ArgumentGroup
from quick.commands.base import Group
from quick.commands.base import ManagerCommand


TYPE_CONVERSION = {
    "int": QuickTopicType.INTEGER,
    "long": QuickTopicType.LONG,
    "string": QuickTopicType.STRING,
    "double": QuickTopicType.DOUBLE,
    "schema": QuickTopicType.SCHEMA,
}


def write_type_from_arg(immutable):
    return TopicWriteType.MUTABLE if immutable is None or not immutable else TopicWriteType.IMMUTABLE


class CreateTopic(ManagerCommand):
    name = "create"
    help = "Create a new topic"

    def execute(self):
        self.validate_deployment_name(self.args.topic_name)
        write_type = write_type_from_arg(self.args.immutable)
        creation_data = TopicCreationData(write_type=write_type)
        params = {
            "key_type": TYPE_CONVERSION[self.args.key_type],
            "value_type": TYPE_CONVERSION[self.args.value_type],
        }
        if params["value_type"] == QuickTopicType.SCHEMA:
            if self.args.schema is None:
                self.parser.error("Please specify a schema with -s/--schema.")

            splits = self.args.schema.split(".")
            if len(splits) != 2:
                self.parser.error("Please specify schema as: GATEWAY.TYPE")

            creation_data.value_schema = GatewaySchema(splits[0], splits[1])

        if self.args.retention_time is not None:
            # check for correct formatting
            isodate.parse_duration(self.args.retention_time)
            creation_data.retention_time = self.args.retention_time

        params["topic_creation_data"] = creation_data
        self.client.create_new_topic(self.args.topic_name, **params)
        print(f"Created new topic {self.args.topic_name}")

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not create new topic: {self.args.topic_name}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("topic_name", metavar="NAME", type=str, help="The name of the topic")
        required.add_argument(
            "-k",
            "--key-type",
            dest="key_type",
            metavar="TYPE",
            type=str.lower,
            choices=TYPE_CONVERSION.keys(),
            help="The key type of the topic",
            required=True,
        )
        required.add_argument(
            "-v",
            "--value-type",
            dest="value_type",
            metavar="TYPE",
            type=str.lower,
            choices=TYPE_CONVERSION.keys(),
            help="The value type of the topic",
            required=True,
        )
        optional.add_argument(
            "-s",
            "--schema",
            dest="schema",
            metavar="SCHEMA",
            type=str,
            help="The schema of the topic defined by gateway's GraphQL type: gateway.type",
        )
        # TODO add partition size as new argument
        # TODO disable automatic mirror creation
        optional.add_argument(
            "--immutable",
            dest="immutable",
            action="store_true",
            help="An immutable topic does not allow ingesting the same key twice (default: False)",
        )
        optional.add_argument(
            "--retention-time",
            type=str,
            help="Retention time of data in the topic in (if not given, the data is kept indefinitely)",
        )


class DeleteTopic(ManagerCommand):
    name = "delete"
    help = "Delete a topic"

    def execute(self):
        self.client.delete_topic(self.args.topic_name)
        print(f"Deleted topic {self.args.topic_name}")

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not delete topic {self.args.topic}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("topic_name", metavar="NAME", type=str, help="Topic to delete")


class ListTopic(ManagerCommand):
    name = "list"
    help = "List all topics"

    def execute(self):
        topics = self.client.list_all_topics()
        for topic in topics:
            print(topic.name)

    def client_error_message(self, exception: ApiException) -> str:
        return (
            "There are no topics registered. "
            "Please create one using: \n\t $ quick topic create <NAME> -k <TYPE> -v <TYPE>"
        )

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        pass


class DescribeTopic(ManagerCommand):
    name = "describe"
    help = "Display information for a topic"

    def execute(self):
        topic = self.client.get_topic_information(self.args.topic_name)
        print("Name: " + topic.name)
        print("Key Type: " + topic.key_type)
        print("Value Type: " + topic.value_type)
        print("Write Type: " + topic.write_type)
        if topic.schema is not None:
            print("Schema:\n" + topic.schema)

    def client_error_message(self, exception: ApiException) -> str:
        return (
            f"There is no topic {self.args.topic_name} registered. "
            f"Please create one: \n\t $ using quick topic create <NAME> -k <TYPE> -v <TYPE>"
        )

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("topic_name", metavar="NAME", type=str, help="The name of the topic.")


class TopicGroup(Group):
    name = "topic"
    help = "Manage topics"

    sub_parser = [CreateTopic, DeleteTopic, ListTopic, DescribeTopic]
