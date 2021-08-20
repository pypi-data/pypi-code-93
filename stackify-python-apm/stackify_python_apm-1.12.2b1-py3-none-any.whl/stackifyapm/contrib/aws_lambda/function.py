from stackifyapm.contrib.aws_lambda import HandlerWrapper


@HandlerWrapper()
def handler(event, context):
    # Proxy handler to initialize HandlerWrapper before running the function
    # for performance purposes
    pass
