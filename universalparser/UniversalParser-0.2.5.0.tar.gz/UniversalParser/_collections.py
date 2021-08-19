from collections import OrderedDict

class ChainDict(OrderedDict):

    cdata_key = 'text_'

    def __init__(self):
        super(ChainDict, self).__init__()

    def __getattr__(self, name):
        if not name.startswith('_'):
            if isinstance(self[name], dict) and 1 == len(self[name]) and self.cdata_key in self[name]:
                return self[name][self.cdata_key]
            else:
                return self[name]
        return super(ChainDict, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name == self.cdata_key:
            pass
        if not name.startswith('_'):
            self[name] = value
        else:
            super(ChainDict, self).__setattr__(name, value)
