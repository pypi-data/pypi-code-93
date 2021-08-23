import json
import sys

from discordbot.api import *
from discordbot import error

class Payload:
    def __init__(self, cereal = None, raw = None):
        if raw is None:
            try:
                self.raw = json.loads(cereal)
            except BaseException as e:
                raise error.ReceivedInvalidPayload("Invalid JSON: %s" % cereal)
        else:
            self.raw = raw
        
        if not "d" in self.raw or not "op" in self.raw:
            raise error.ReceivedInvalidPayload("Did not receive 'd' and 'op' fields: %s" % cereal)
        
        self.opcode = self.raw["op"]
        self.data = self.raw["d"]
        if opcode.get_name(self.opcode) is None:
            raise error.ReceivedInvalidPayload("Invalid opcode: %s" % self.opcode)
    
    def __str__(self):
        return json.dumps(self.raw)
    __repr__ = __str__

class Event(Payload):
    def __init__(self, pl):
        super().__init__(raw = pl.raw)
        
        if not 's' in self.raw or not 't' in self.raw:
            raise error.ReceivedInvalidPayload("Did not receive 's' and 't' fields: %s" % self)
        
        self.sequence = self.raw['s']
        self.name = self.raw['t']

class ReadyEvent(Event):
    def __init__(self, evt):
        super().__init__(evt)
        
        if not 'user' in self.data or not 'session_id' in self.data:
            raise error.ReceivedInvalidPayload("Did not receive 'user' and 'session_id' data: %s" % str(self.data))
        
        self.session_id = self.data['session_id']
        try:
            self.user = structure.User(self.data['user'])
        except error.InvalidAPIObject as e:
            raise error.ReceivedInvalidPayload("Bad user: %s" % str(e))

class GuildCreateEvent(Event):
    def __init__(self, evt):
        super().__init__(evt)
        
        try:
            self.guild = structure.Guild(self.data)
        except error.InvalidAPIObject as e:
            raise error.ReceivedInvalidPayload("Bad guild: %s" % str(e))

class MessageCreateEvent(Event):
    def __init__(self, evt):
        super().__init__(evt)
        
        try:
            self.message = structure.Message(self.data)
        except error.InvalidAPIObject as e:
            raise error.ReceivedInvalidPayload("Bad message: %s" % str(e))
            
class MessageEditEvent(Event):
    def __init__(self, evt):
        super().__init__(evt)
        
        try:
            self.before = None
            if 'id' in self.data and str(self.data['id']) in structure.Message.cache:
                # make a copy of the cached version
                raw = structure.Message.cache[str(self.data['id'])].raw
                self.before = structure.Message(raw)
            
            # load new version (and cache it)
            self.after = None
            try:
                self.after = structure.Message(self.data)
            except error.InvalidAPIObject as e:
                # rip, discord didn't send the whole message
                # just make sure that the bot will be able to retrieve it via the REST api
                if not "id" in self.data:
                    raise error.ReceivedInvalidPayload("MessageEditEvent did not receive required field 'id'")
                if not "channel_id" in self.data:
                    raise error.ReceivedInvalidPayload("MessageEditEvent did not receive required field 'channel_id'")
        except error.InvalidAPIObject as e:
            raise error.ReceivedInvalidPayload("Bad message: %s" % str(e))

class MessageDeleteEvent(Event):
    def __init__(self, evt):
        super().__init__(evt)
        
        try:
            self.message = None
            if str(self.data['id']) in structure.Message.cache:
                self.message = structure.Message.cache[str(self.data['id'])]
        except error.InvalidAPIObject as e:
            raise error.ReceivedInvalidPayload("Bad message: %s" % str(e))

class MessageBulkDeleteEvent(Event):
    def __init__(self, evt):
        super().__init__(evt)
        
        try:
            self.channel = structure.Channel({"id": self.data["channel_id"]})
            self.guild = structure.Guild({"id": self.data["guild_id"]})
            
            self.messages = []
            
            for id in self.data["ids"]:
                if str(id) in structure.Message.cache:
                    self.messages.append(structure.Message.cache[str(id)])
                else:
                    self.messages.append({"id": id})
        except error.InvalidAPIObject as e:
            raise error.ReceivedInvalidPayload("Bad message: %s" % str(e))

class Hello(Payload):
    def __init__(self, pl):
        super().__init__(raw = pl.raw)
        
        if not 'heartbeat_interval' in self.data:
            raise error.ReceivedInvalidPayload("Did not receive 'heartbeat_interval' field: %s" % self)
        
        self.heartbeat_interval = self.data['heartbeat_interval'] / 1000

class OutgoingPayload:
    def dumps(self):
        return json.dumps({
            'op': self.opcode,
            'd': self.data
        })

class OutgoingHeartbeat(OutgoingPayload):
    def __init__(self, sequence):
        self.opcode = opcode.heartbeat
        self.data = sequence

class OutgoingIdentify(OutgoingPayload):
    def __init__(self, token, intents, identifier):
        self.opcode = opcode.identify
        self.data = {
            "token": token,
            "properties": {
                "$os": sys.platform,
                "$browser": str(identifier),
                "$device": str(identifier),
            },
            "intents": intents
        }

class Resume(OutgoingPayload):
    def __init__(self, token, session_id, sequence):
        self.opcode = opcode.resume
        self.data = {
            "token": token,
            "session_id": session_id,
            "seq": sequence
        }