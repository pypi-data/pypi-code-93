from argparse import ArgumentParser
from argparse import FileType

from quick_client import ApiException
from quick_client import GatewayCreationData
from quick_client import SchemaData

from quick.commands.base import ArgumentGroup
from quick.commands.base import Group
from quick.commands.base import ManagerCommand


class CreateGateway(ManagerCommand):
    name = "create"
    help = "Create a gateway"

    def execute(self):
        self.validate_deployment_name(name=self.args.gateway_name)
        if self.args.schema is not None:
            with self.args.schema as file:
                schema = file.read()
        else:
            schema = None

        creation_data = GatewayCreationData(replicas=self.args.replicas, tag=self.args.tag, schema=schema)
        self.client.create_gateway(self.args.gateway_name, gateway_creation_data=creation_data)
        print(f"Create gateway {self.args.gateway_name} (this may take a few seconds)")

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not create gateway {self.args.gateway_name}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("gateway_name", metavar="NAME", type=str, help="Name of the gateway")
        optional.add_argument(
            "--replicas",
            metavar="REPLICAS",
            type=int,
            help="Number of replicas",
            required=False,
        )
        optional.add_argument(
            "--tag",
            metavar="TAG",
            type=str,
            help="Docker image tag (defaults to currently installed tag)",
            required=False,
        )
        required.add_argument(
            "-s",
            "--schema",
            dest="schema",
            metavar="SCHEMA_FILE",
            type=FileType("r"),
            help="Location of the schema file or std in",
            required=False,
        )


class DeleteGateway(ManagerCommand):
    name = "delete"
    help = "Delete a gateway"

    def execute(self):
        self.client.delete_gateway(self.args.gateway_name)
        print(f"Deleted gateway {self.args.gateway_name}")

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not delete gateway {self.args.gateway_name}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("gateway_name", metavar="NAME", type=str, help="Name of the gateway")
        parser.set_defaults(func=self)


class ApplyDefinition(ManagerCommand):
    name = "apply"
    help = "Apply a new schema to a gateway"

    def execute(self):
        with self.args.file as file:
            data = file.read()
        self.client.create_schema(self.args.gateway_name, SchemaData(data))
        print(f"Applied schema to gateway {self.args.gateway_name}")

    def client_error_message(self, exception: ApiException) -> str:
        return f"Could not apply schema to gateway: {self.args.gateway_name}"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("gateway_name", metavar="NAME", type=str, help="Name of the gateway")
        required.add_argument(
            "-f",
            "--file",
            dest="file",
            metavar="FILE",
            type=FileType("r"),
            help="Location of the schema file or std in",
            required=True,
        )


class ListGateway(ManagerCommand):
    """
    The 'list' command prints all the deployed gateways
    """

    name = "list"
    help = "List all gateways"

    def execute(self):
        gateways = self.client.list_all_gateways()
        for gateway in gateways:
            print(gateway.name)

    def client_error_message(self, exception: ApiException) -> str:
        return "There are no gateways created. " "Please create one using:\n\t $ quick gateway create <NAME>"

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        pass


class DescribeGateway(ManagerCommand):
    """
    The 'describe' command prints all information about a gateway
    """

    name = "describe"
    help = "Display information about a gateway"

    def execute(self):
        gateway = self.client.get_gateway(self.args.gateway_name)
        print("Name: " + gateway.name)
        print("Replicas: " + gateway.replicas)
        print("Tag: " + gateway.tag)

    def client_error_message(self, exception: ApiException) -> str:
        return (
            f"There is no gateway {self.args.gateway_name} created. "
            "Please create one using\n\t $ quick gateway create <NAME>"
        )

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("gateway_name", metavar="NAME", type=str, help="The name of the gateway.")


class GatewaySchema(ManagerCommand):
    """
    The 'schema' command prints the schema of a gateway in Avro or GraphQL format
    """

    name = "schema"
    help = "Display the schema of a gateway in Avro or GraphQL format"

    def execute(self):
        if self.args.avro:
            write_schema = self.client.get_avro_write_schema(self.args.gateway_name, self.args.gateway_schema_type)
        else:
            write_schema = self.client.get_graphql_write_schema(self.args.gateway_name, self.args.gateway_schema_type)

        print(write_schema.schema)

    def client_error_message(self, exception: ApiException) -> str:
        return (
            f"There is no gateway {self.args.gateway_name} created. "
            "Please create one using\n\t $ quick gateway create <NAME>"
        )

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("gateway_name", metavar="NAME", type=str, help="The name of the gateway.")
        required.add_argument(
            "gateway_schema_type", metavar="TYPE", type=str, help="The type name used in the gateway schema."
        )
        required.add_argument(
            "--avro",
            action="store_true",
            help="Determines if the returned format should be in Avro " "(If not set GraphQL format is returned).",
            required=False,
        )


class GatewayGroup(Group):
    name = "gateway"
    help = "Manage gateways"

    sub_parser = [CreateGateway, DeleteGateway, ApplyDefinition, ListGateway, DescribeGateway, GatewaySchema]
