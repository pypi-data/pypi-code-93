from argparse import ArgumentParser

from quick_client import ApiException

from quick.commands.base import ArgumentGroup
from quick.commands.base import Group
from quick.commands.base import ManagerCommand


class CreateMirror(ManagerCommand):
    name = "create"
    help = "Mirror a Kafka topic"
    description = "Create a mirror for a topic and make it queryable through a gateway"

    def execute(self):
        self.client.create_mirror(self.args.topic, replicas=self.args.replicas, tag=self.args.tag)
        print(f"Create mirror for topic {self.args.topic} (this may take a few seconds)")

    def client_error_message(self, exception):
        return f"Could not create mirror for topic {self.args.topic}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("topic", metavar="TOPIC", type=str, help="Topic to mirror")
        optional.add_argument(
            "--tag",
            dest="tag",
            metavar="TAG",
            type=str,
            help="Docker image tag (defaults to currently installed tag)",
            required=False,
        )
        optional.add_argument(
            "--replicas",
            dest="replicas",
            metavar="REPLICAS",
            type=int,
            help="Number of replicas (default: 1)",
            required=False,
            default=1,
        )


class DeleteMirror(ManagerCommand):
    name = "delete"
    help = "Delete a mirror"

    def execute(self):
        self.client.delete_mirror(self.args.mirror)
        print(f"Deleted mirror {self.args.mirror}")

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not delete mirror {self.args.mirror}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("mirror", metavar="TOPIC", type=str, help="Topic to delete mirror from")


class MirrorGroup(Group):
    name = "mirror"
    help = "Manage mirrors"
    description = (
        "Mirrors make topics queryable. "
        "With these commands, you can control which topic can be queried through gateway."
    )
    sub_parser = [
        CreateMirror,
        DeleteMirror,
    ]
