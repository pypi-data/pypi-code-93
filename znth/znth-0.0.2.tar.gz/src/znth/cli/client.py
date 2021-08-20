from znth.cli.default import DefaultProcessor
from znth.command.common import ReadlineCommand
from znth.command.database import DatabaseContext
from znth.factory.client import ClientFactory


class ClientProcessor(DefaultProcessor):
    def activate(self, name: str) -> None:
        context = DatabaseContext()
        context["client_name"] = name

        runner = ClientFactory.create_activate(self.log_level)
        runner.execute(context)

    def create(self, name: str) -> None:
        context = DatabaseContext()
        context["client_name"] = name

        runner = ClientFactory.create_create(self.log_level)
        runner.execute(context)

    def read(self, name: str) -> None:
        context = DatabaseContext()
        context["client_name"] = name

        runner = ClientFactory.create_read(self.log_level)
        runner.execute(context)

        self.display(context)

    def update(self, name: str) -> None:
        context = DatabaseContext()
        context["client_name"] = name

        runner = ClientFactory.create_read(self.log_level)
        runner.execute(context)

        client = context["client"]
        context["client_description"] = self.input("Description: ", client.client_description)
        context["client_remark"] = self.input("Remark: ", client.client_remark)

        runner = ClientFactory.create_update(self.log_level)
        runner.execute(context)

        runner = ClientFactory.create_client_read(self.log_level)
        runner.execute(context)

        self.display(context)

    def delete(self, name: str) -> None:
        context = DatabaseContext()
        context["client_name"] = name

        runner = ClientFactory.create_delete(self.log_level)
        runner.execute(context)

    def list(self) -> None:
        context = DatabaseContext()

        runner = ClientFactory.create_list(self.log_level)
        runner.execute(context)

        self.display(context)

    def display(self, context: DatabaseContext) -> None:
        if "client" in context:
            client = context["client"]
            print(f"""\
ID:          {client.client_id}
UUID:        {client.client_uuid}
Name:        {client.client_name}
Active:      {client.client_active}
Description: {client.client_description or ''}

{client.client_remark or ''}""")
        elif "clients" in context:
            clients = context["clients"]
            for client in clients:
                if client.client_active:
                    msg = f"+ {client.client_id} + {client.client_name} + {client.client_uuid}"
                else:
                    msg = f"- {client.client_id} - {client.client_name} - {client.client_uuid}"
                print(msg)


if __name__ == "__main__":
    processor = ClientProcessor()
    while True:
        line = processor.input("Test: ", "Een test waarde.")
        print(f"Line: {line}")
        if line == "stop":
            break