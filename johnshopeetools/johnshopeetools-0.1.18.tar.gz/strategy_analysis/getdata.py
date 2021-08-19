from pyhive import presto
import pandas as pd
import numpy as np

class getdata:
    def get_query_from_file(self, filepath):
        fd = open(filepath, 'r')
        query = fd.read()
        return query

    def run_shopee_presto(self, query, conn):
        """
        get shopee data from presto using jdbc
        """
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        desc = cur.description
        col_name = [x[0] for x in desc]

        df = pd.DataFrame(rows, columns=col_name)

        return df