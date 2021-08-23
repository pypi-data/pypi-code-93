import os
import pymssql
from typing import Dict, List
from collections import Counter

PWD= os.getcwd()
SOURCE_TABLES_PATH = os.path.join(PWD, 'sourceTables')
SPARKSQL_TABLES_PATH = os.path.join(PWD, 'sparkTables')
CTL_SELECT_PATH = os.path.join(PWD, 'ctlSelectS')
if not os.path.exists(SOURCE_TABLES_PATH):
    os.mkdir(SOURCE_TABLES_PATH)
if not os.path.exists(SPARKSQL_TABLES_PATH):
    os.mkdir(SPARKSQL_TABLES_PATH)
if not os.path.exists(CTL_SELECT_PATH):
    os.mkdir(CTL_SELECT_PATH)


class Utils:
    
    @staticmethod
    def rename(s):
        s = s.lower()
        s = s.replace(' ', '_')
        output = ''
        for ch in s:
            if ch in '0123456789' or ch.isalpha():
                output += ch
            else:
                output += '_'
        while '__' in output:
            output = output.replace('__', '_')

        return output

    @staticmethod
    def check_unique(original_table_name: str, s: list):
        c = Counter(s)
        for k, v in dict(c).items():
            if v > 1:
                print(original_table_name, k, v)
    
    @staticmethod
    def transform_type(s):
        s = s.strip()
        if s.startswith('nvarchar') or s.startswith('varchar') or s.startswith('char'):
            return 'string'
        if s.startswith('bit'):
            return 'boolean'
        if s.startswith('datetime'):
            return 'timestamp'

        return s
    

class DbSchemaTables:
    __slots__ = ['db', 'schema', 'table_name']
    
    def __init__(self, db:str = '', schema:str = '', table_name: str = ''):
        if db == '' or schema == '' or table_name == '':
            raise Exception('db or schema or table_name should not be empty')
        self.db = db
        self.schema = schema
        self.table_name = table_name

        
class SparkDbSchemaTables:
    __slots__ = ['db_tmp', 'db_hz', 'table_name']
    
    def __init__(self, db_tmp:str = '', db_hz:str = '', table_name: str = ''):
        if db_tmp == '' or db_hz == '' or table_name == '':
            raise Exception('db_tmp or db_hz or table_name should not be empty')
        self.db_tmp = db_tmp
        self.db_hz = db_hz
        self.table_name = table_name

def gen_db_schema_table(db:str, schema:str, table_name:str)->DbSchemaTables:
    return DbSchemaTables(db, schema, table_name)



class GenTableMappingFromSourceTables:
    
    __slots__ =['sqlconfig']
    """
    mapping tables stored in sourceTables
    
    """
    
    def __init__(self, sqlconfig: Dict):
        self.sqlconfig = sqlconfig
    
    
    def gen_sql_mapping(self, msconfig: Dict, dbsts: List[DbSchemaTables]):
        conn = pymssql.connect(**msconfig)
        fsql = """SELECT COLUMN_NAME, DATA_TYPE , CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{}' and TABLE_SCHEMA = '{}' and TABLE_CATALOG = '{}' """
        cursor = conn.cursor()
        for dbst in dbsts:
            sql = fsql.format(dbst.table_name, dbst.schema, dbst.db)
            path = os.path.join(SOURCE_TABLES_PATH, dbst.table_name + '.csv')
            try:
                cursor.execute(sql)
                results = cursor.fetchall()
                columns = []
                with open(path, 'w') as f:
                    for r in results:
                        f.write(f"""{r[0]}, {r[1]}, {r[2]}\n""")
                        columns.append(r[0])
                self.save_select_sql(dbst.table_name, dbst.db, dbst.schema, columns)
            except Exception as err:
                conn.close()
                print(err)
                print('continue')
        conn.close()
        
    @staticmethod
    def read_db_schem_tables_from_file(filename: str) -> List[DbSchemaTables]:
        configs = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                db, schema, table_name = line.split(',')
                configs.append(DbSchemaTables(db, schema, table_name))
        return configs
    
    
    @staticmethod
    def save_select_sql(table_name: str, db: str, schema: str, columns: List):
        columns_ = [f'[{x}]' for x in columns]
        path = os.path.join(CTL_SELECT_PATH, table_name.lower() +'.sql')
        sql = f"""select {','.join(columns_)} from {db}.{schema}.{table_name}"""
        with open(path, 'w') as f:
            f.write(sql)
    
    def run(self, filename:str):
        self.gen_sql_mapping(self.sqlconfig, self.read_db_schem_tables_from_file(filename))
        

class GenSparkSqlFromLocalMappingTables:
    
    """
    generate spark sql by reading files from folder sparkTables
    """
    
    @staticmethod
    def create_spark_sql(args: Dict, template:str = None):
        if template is None:
            return """
create database if not exists {db_tmp};

drop table if exists {db_tmp}.{table_name};

CREATE TABLE
if not exists {db_tmp}.{table_name}(
{column_mapping})
USING com.databricks.spark.csv
  options(PATH = '${{lz_blob_path}}/{table_name}', sep = ',', nullValue='\\\\N',header = 'false');

create database if not exists {db_hz};

CREATE TABLE
if not exists {db_hz}.{table_name}(
{column_mapping})
partitioned by ( src_sys_region_nm string, partition_date bigint)
  options(PATH = '${{hz_blob_path}}/{table_name}');

insert overwrite {db_hz}.{table_name} PARTITION (src_sys_region_nm ='china', partition_date = '${{partition_date}}')
select * from {db_tmp}.{table_name};

drop table if exists {db_tmp}.{table_name};
    """.format(**args)
        
        else:
            return template.format(**args)
    
    @staticmethod
    def save_spark_sql(table_name:str, sql:str):
        save_path = os.path.join(SPARKSQL_TABLES_PATH, table_name +'.sql')
        with open(save_path, 'w') as f:
            f.write(sql)
    
    @staticmethod
    def read_db_schem_tables_from_file(filename: str) -> List[SparkDbSchemaTables]:
        configs = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                db_tmp, db_hz, table_name = line.split(',')
                configs.append(SparkDbSchemaTables(db_tmp, db_hz, table_name))
        return configs
    
    @staticmethod
    def read_and_generate_columns_mapping(table_name:str) ->str:
        """
        return： (sparksql fields,  select fields)
        """
        path = os.path.join(SOURCE_TABLES_PATH, table_name +'.csv')
        columns = []
        column_mapping = []
        
        with open(path, 'r') as f:
            for line in f.readlines():
                column, col_type, col_length = line.split(',')
                re_name = Utils().rename(column)
                columns.append(re_name)
                column_mapping.append(f"""`{re_name}` {Utils().transform_type(col_type)} comment "{column}" """)
        
        Utils().check_unique(table_name, columns)
        sql_line = ',\n'.join(column_mapping)
        return sql_line
    
    def run(self, filename:str):
        for sdst in self.read_db_schem_tables_from_file(filename):
            table_name  = sdst.table_name
            db_tmp = sdst.db_tmp
            db_hz  = sdst.db_hz
            args  = {
                'table_name': table_name.lower(),
                'db_tmp': db_tmp,
                'db_hz': db_hz,
                'column_mapping': self.read_and_generate_columns_mapping(table_name)
            }
            sql = self.create_spark_sql(args)
            self.save_spark_sql(table_name.lower(), sql)

