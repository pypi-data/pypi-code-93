__all__ = ("minify_graphql_call",)


def minify_graphql_call(call: str) -> str:
    """
    Minify GraphQL call.

    Right now this just strips leading whitespace from all lines
    which is enough to reduce size by ~50%.
    """
    return "\n".join(line.lstrip() for line in call.strip().splitlines())
