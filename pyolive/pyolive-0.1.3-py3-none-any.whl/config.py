import os
import configparser


class Config:
    def __init__(self, name, section):
        home = os.getenv('OLIVE_HOME')
        if home is None:
            print("Not found environment variable, OLIVE_HOME")
        self.cf = configparser.RawConfigParser()
        self.cf.read(os.path.join(home, 'config', name))
        self.section = section

    def get_keys(self):
        return self.cf[self.section]

    def get_value(self, key):
        _s1 = self.cf[self.section][key]
        _s2 = _s1.split('#')
        return _s2[0].strip()
