import pymysql
import datetime
import decimal


def format_sql_insert(M):
    fields = []
    values = []
    for key in M.keys():
        value = M[key]
        fields.append(key)
        append_value(values, key, value)
    return ",".join(fields), ",".join(values)


def format_sql_update(M):
    return format_sql_where(M, relation=",")


def append_value(values, key, value):
    if type(value) == int:
        values.append(str(value))
    elif type(value) == float:
        values.append(str(value))
    elif type(value) == decimal.Decimal:
        values.append(str(value))
    elif not value:
        values.append("''")
    else:
        if isinstance(value, str):
            if is_db_func(value) or value.lower() == "null":
                values.append(value)
            elif key in value and check_contains(value, ["||", "&"]):
                values.append(value)
            else:
                values.append("'" + pymysql.escape_string(value) + "'")
        elif type(value) == datetime.datetime:
            values.append("'" + str(value) + "'")
        else:
            values.append(str(value))


def is_db_func(value):
    if value.startswith("ST_") or value.startswith("st_"):
        return True
    if value.endswith(")") and "(" in value:
        func_name = value[value.index("("):]
        func_name = func_name.lower()
        if func_name in [""]:
            return True
    return False


def check_contains(value, char_list):
    for char in char_list:
        if char in value:
            return True
    return False


def format_sql_where(M, option="=", relation="and"):
    fields = []
    values = []
    L = []
    for key in M.keys():
        value = M[key]
        fields.append(key)
        append_value(values, key, value)
        L.append('{}{}{}'.format(fields[-1], option, values[-1]))
    return f" {relation} ".join(L)
