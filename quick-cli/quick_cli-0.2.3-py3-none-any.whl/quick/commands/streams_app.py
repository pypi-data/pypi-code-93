from argparse import ArgumentParser

from quick_client import ApiException

from quick.commands.base import ArgumentGroup
from quick.commands.base import Group
from quick.commands.base import ManagerCommand
from quick.parser import ArgsAction


class DeployStreamsApp(ManagerCommand):
    name = "deploy"
    help = "Deploy a new application"
    description = (
        "Deploy a new application. "
        "\n"
        "The application must be provided as a Docker image. "
        "You can specify the registry."
    )

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not create application: {exception.body}"

    def execute(self):
        request_body = {} if self.args.props is None else self.args.props

        self.client.deploy_application(
            name=self.args.application_name,
            registry=self.args.registry,
            image_name=self.args.image,
            tag=self.args.tag,
            replicas=self.args.replicas,
            request_body=request_body,
        )
        print(f"Deployed application {self.args.application_name}")

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument(
            "application_name", metavar="NAME", type=str, help="Name of the application (must be unique)"
        )
        required.add_argument(
            "--registry",
            metavar="REGISTRY_URL",
            type=str,
            help="URL to container registry",
            required=True,
        )
        required.add_argument("--image", metavar="IMAGE", type=str, help="Name of the image", required=True)
        required.add_argument(
            "--tag",
            metavar="TAG",
            type=str,
            help="Docker image tag",
            required=True,
        )
        optional.add_argument(
            "--replicas",
            metavar="REPLICAS",
            type=int,
            help="Number of replicas",
            required=False,
            default=1,
        )
        optional.add_argument(
            "--args",
            dest="props",
            metavar="ARG=VALUE",
            required=False,
            action=ArgsAction,
            nargs="*",
            help="CLI arguments of the application (broker and schema registry not required)",
        )


class DeleteStreamsApp(ManagerCommand):
    name = "delete"
    help = "Delete an application"
    description = "Delete an application. This stops the running Streams application and removes all its state."

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not delete application {self.args.application_name}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("application_name", metavar="NAME", type=str, help="Name of the application")

    def execute(self):
        self.client.delete_application(name=self.args.application_name)
        print(f"Deleted application {self.args.application_name}")


class StreamsAppGroup(Group):
    name = "app"
    help = "Manage streams applications"
    description = (
        "Streams applications are Kafka Streams applications processing your data stream. "
        "You can deploy them to the quick cluster."
    )
    sub_parser = [
        DeployStreamsApp,
        DeleteStreamsApp,
    ]
