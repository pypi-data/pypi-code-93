def post(hub, ctx):
    """
    Conform the output of every state return to this format.
    Valid state modules must return a dictionary with these keys
    """
    try:
        return {
            "changes": ctx.ret["changes"],
            "comment": ctx.ret["comment"],
            "name": ctx.ret["name"],
            "result": ctx.ret["result"],
        }
    except KeyError:
        hub.log.error(f"Improperly formatted state return: {ctx.ref}")
        raise
