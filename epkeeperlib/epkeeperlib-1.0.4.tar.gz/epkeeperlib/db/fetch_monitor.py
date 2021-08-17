from mysql_pool import mysql_fetch_data


def get_oa_monitor_data(sn, oa_monitor_db_config, start_time=None, end_time=None, line=None, cols=None):
    where_sql = ""

    if start_time and end_time:
        where_sql = " WHERE tm >= '%s' AND tm < '%s' " % (start_time, end_time)
    elif start_time and not end_time:
        where_sql = " WHERE tm >= '%s' " % start_time
    elif not start_time and end_time:
        where_sql = " WHERE tm <= '%s' " % end_time

    if line:
        if where_sql:
            where_sql += " AND line=%s " % line
        else:
            where_sql = " WHERE line=%s " % line

    if cols is None:
        cols = "*"
    else:
        cols = ",".join(cols)
    table = "tb_%s" % sn
    sql = """
    SELECT {cols} FROM {table} {where_sql}
    """.format(cols=cols, table=table, where_sql=where_sql)
    data = mysql_fetch_data(oa_monitor_db_config, sql)
    return data

