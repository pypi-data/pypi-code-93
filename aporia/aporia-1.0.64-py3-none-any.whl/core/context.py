from .config import Config
from .errors import AporiaError
from .event_loop import EventLoop
from .graphql_client import GraphQLClient

global_context = None


class Context:
    """Global context."""

    def __init__(
        self,
        graphql_client: GraphQLClient,
        event_loop: EventLoop,
        config: Config,
    ):
        """Initializes the context.

        Args:
            graphql_client (GraphQLClient): GraphQL client.
            event_loop (EventLoop): Event loop.
            config (Config): Aporia config.
        """
        self.graphql_client = graphql_client
        self.event_loop = event_loop
        self.config = config

        self._open_graphql_client()

    def _open_graphql_client(self):
        self.event_loop.run_coroutine(self.graphql_client.open())

    def shutdown(self):
        """Cleans up objects managed by the context."""
        self.event_loop.run_coroutine(self.graphql_client.close())


def init_context(graphql_client: GraphQLClient, event_loop: EventLoop, config: Config):
    """Initializes the global context.

    Args:
        graphql_client (GraphQLClient): GraphQL client
        event_loop (EventLoop): Event loop
        config (Config): Configuration
    """
    global global_context

    global_context = Context(graphql_client=graphql_client, event_loop=event_loop, config=config)


def reset_context():
    """Resets the global context."""
    global global_context
    if global_context is None:
        raise AporiaError("Aporia was not initialized.")

    global_context.shutdown()
    global_context = None


def get_context() -> Context:
    """Returns the global context."""
    if global_context is None:
        raise AporiaError("Aporia was not initialized.")

    return global_context
