import dask as dd

def send_table(input_table, uri_input, output_table, uri_output, schema, parallel = True, method='multi', chunksize = 50_000, if_exists = 'append'):
    df = dd.read_sql(table = input_table, uri = uri_input)
    dd.to_sql(df,uri=uri_output, name=output_table, schema=schema, parallel=parallel, method='multi',chunksize=chunksize,if_exists=if_exists)


def migrate(uri_origin, uri_destiny, destiny_schema):
    def output_func(table_origin, table_destiny, index_column, parallel=True, method='multi',chunksize = 30_000, if_exists='replace'):
        df = dd.read_sql(table = table_origin, uri = uri_origin, index_column = index_column)
        dd.to_sql(df,uri=uri_destiny, name=table_destiny, schema=destiny_schema, parallel=parallel, method='multi',chunksize=chunksize,if_exists=if_exists)    
    return output_func