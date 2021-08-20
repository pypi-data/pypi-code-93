import logging
import uuid

from znth.chain import Command, Context

class NodeUUIDCommand(Command):
    def execute(self, context: Context) -> bool:
        logger = logging.getLogger(__name__)
        logger.debug("uuid.execute() - Start")

        context["node_uuid"] = str(uuid.UUID(int=uuid.getnode()))

        logger.info(f"Node UUID: {context['node_uuid']}")
        logger.debug("uuid.execute() - Finish")
        return Command.SUCCESS

if __name__ == "__main__":
    context = Context()
    command = NodeUUIDCommand()
    command.execute(context)

    print(f"Node UUID: {context['node_uuid']}")
