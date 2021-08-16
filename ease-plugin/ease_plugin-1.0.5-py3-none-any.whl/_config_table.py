from ease_sqlite.Squtils import *


class config(SqTable, metaclass=TableMeta):
    UPDATE_METHOD = UPDATE_METHOD.CHANGE_RENAME
    
    plugin_name = TEXT_Sqlite
    plugin_state = INT_Sqlite

    @classmethod
    def Constraint(cls):
        cls.PLUGIN_NAME = [cls.plugin_name]
