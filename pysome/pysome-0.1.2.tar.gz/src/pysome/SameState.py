class default_name:
    def __hash__(self):
        return hash(str(self))


class SameState:
    _allow = {
        "Same": False,
        "NotSame": False
    }
    _state = {
        "Same": {},
        "NotSame": {}
    }

    @staticmethod
    def _start():
        for key in SameState._allow.keys():
            SameState._allow[key] = True
            SameState._state[key] = {}

    @staticmethod
    def _end():
        for key in SameState._allow.keys():
            SameState._allow[key] = False
            SameState._state[key] = {}
