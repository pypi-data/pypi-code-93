class Base:
    def __init__(self, *args):
        self.args = args

class ready(Base):
    # the bot has completed:
    #   - connected to the websocket
    #   - authenticated to the gateway
    #   - received a hello payload
    #   - sent a heartbeat payload
    #   - received a heartbeat ack payload
    
    # args are: ()
    pass

class guild_message_sent(Base):
    # a message was sent in a guild
    # args are: (message: api.structure.Message)
    pass

class guild_message_edited(Base):
    # a message was edited in a guild
    # args are: (before: api.structure.Message, after: api.structure.Message)
    pass

class guild_message_deleted(Base):
    # a message was deleted in a guild
    # args are: (message: api.structure.Message)
    pass

class guild_message_bulk_delete(Base):
    # several messages were deleted at once
    # the argument is an array of messages,
    # elements of which are either a dict containing
    # just the id, or a Message structure (if it was cached)
    pass
    
class guild_created(Base):
    # when the bot joins a guild
    # args are: (guild: api.structure.Guild)
    pass