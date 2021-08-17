event = 0
heartbeat = 1
identify = 2
update_presence = 3
update_voice_state = 4
resume = 6
reconnect = 7
request_members = 8
session_invalidated = 9
hello = 10
heartbeat_ack = 11

_all_opcodes = {
    'event': event,
    'heartbeat': heartbeat,
    'identify': identify,
    'update_presence': update_presence,
    'update_voice_state': update_voice_state,
    'resume': resume,
    'reconnect': reconnect,
    'request_members': request_members,
    'session_invalidated': session_invalidated,
    'hello': hello,
    'heartbeat_ack': heartbeat_ack,
}
def get_name(opcode):
    if not isinstance(opcode, int):
        return None
    for name in _all_opcodes:
        if _all_opcodes[name] == opcode:
            return name
    return None