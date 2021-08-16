
def table(table_name):
    def decorator(en_cls):
        en_cls.init_table(table_name)
        return en_cls

    return decorator