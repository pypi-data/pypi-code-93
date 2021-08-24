import pandas as pd
import sqlalchemy
import json
import logging

logger = logging.getLogger(__name__)

def get_new_ids(table, col, con, count=1):
    """Requests new unique ID:s from a primary key column so that they can
       be inserted on the python side into a dataframe that will be
       appended to the table, and in foreign key columns in other
       dataframes.

       table = table name
       col = primary key column name
       con = sqlalchemy connection
       count = number of ID:s to generate, defaults to 1

       Returns pandas Series of count ID:s.
    """
    seq = sqlalchemy.Sequence("%s_%s_seq" % (table, col))
    try:
        res = pd.DataFrame(con.execute(
            sqlalchemy.select(
                [seq.next_value()]
            ).select_from(
                sqlalchemy.func.generate_series(1, count)
            )))[0]
        return res
    except sqlalchemy.exc.ProgrammingError as e:
        if not "UndefinedTable" in str(e):
            raise
        con.execute(sqlalchemy.schema.CreateSequence(seq))
        return get_new_ids(table, col, con, count=count)

def to_sql(df, name, con, keycols=[], references={}, chunksize=4096, method="multi", basecols=None, **kw):
    """Like pd.DataFrame().to_sql, but supports auto-increment unique key
       columns, foreign key columns, and automatic JSONification of extraneous columns.

       keycols = ["colname1", "colname2", ...]
           Columns to add a database level default value of an
           autoincrement sequence. The columns do not need to, but
           can, exist in the dataframe.
       references = {"colname": "desttable.destcolname", ...}
           Columns to add a foreign key constraint to. Columns must
           exist in the dataframe, and the destination table and
           column must already exist.
       basecols = ["colname1", "colname2", ...]
           Only use these columns to form the table. Any other columns
           will be stored in a JSON object per row in the column
           "extra".
    """
    
    if basecols is not None:
        df = df.assign(**{missing: None
                          for missing in set(basecols) - set(df.columns)})
        extra = df[set(df.columns) - set(basecols)]
        df = df[basecols].copy()
        df["extra"] = extra.apply(
            lambda r: json.dumps(
                {key:value.item()
                 if hasattr(value, "dtype")
                 else value
                 for key, value in r.items()}), axis=1)
        df["extra"] = df["extra"].astype("object")

    pandastable = pd.io.sql.SQLTable(name, pd.io.sql.SQLDatabase(con), frame=df, if_exists="append", **kw)
    table = pandastable.table.tometadata(sqlalchemy.MetaData(con))
    
    for key, ref in references.items():
        ref_table, ref_col = ref.split(".")
        logger.debug("For table %s, col %s -> ref table: %s, ref col: %s" % (name, key, ref_table, ref_col))
        reftable = sqlalchemy.Table(
            ref_table, table.metadata,
            sqlalchemy.Column(ref_col, sqlalchemy.BigInteger(), primary_key=True))
        references[key] = reftable.columns[ref_col]
        
    seqs = []
    for keycol in keycols:
        seq = sqlalchemy.sql.schema.Sequence('%s_%s_seq' % (pandastable.name, keycol))
        seqs.append(seq)
        if keycol not in table.columns:
            table.append_column(sqlalchemy.Column(keycol, sqlalchemy.BigInteger()))    
        keycoldef = table.columns[keycol]
        table.append_constraint(sqlalchemy.sql.schema.UniqueConstraint(keycol))
        keycoldef.server_default = sqlalchemy.DefaultClause(seq.next_value())

    for key, ref in references.items():
        table.append_constraint(sqlalchemy.ForeignKeyConstraint([key], [ref]))        

    for seq in seqs:
        seq.create(con)
    # table.create()

    table.metadata.create_all(checkfirst=True)
    
    pandastable.insert(chunksize=chunksize, method=method)

def expand_json_column(df, col):
    if len(df) == 0: return
    content = df[col].apply(lambda e: json.loads(e) if e else {})
    content_keys = list(content[0].keys())
    for key in content_keys:
        df[key] = content.apply(lambda r: r[key])
    del df[col]
    return content_keys

def read_sql_query(
    sql,
    con,
    index_col=None,
    coerce_float=True,
    params=None,
    parse_dates=None,
    chunksize = None):
    """Like pd.read_sql_query, but supports deserializing extra columns
       from a column `extra` containing JSON objects.
    """
    if params is not None:
        p = []
        for param in params:
            if hasattr(param, "dtype"):
                param = param.item()
            p.append(param)
        params = p
    df = pd.read_sql_query(
        sql,
        con,
        index_col,
        coerce_float,
        params,
        parse_dates,
        chunksize)
    if "extra" in df.columns:
        expand_json_column(df, "extra")
    return df
