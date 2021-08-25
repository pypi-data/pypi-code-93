import os

PWD = os.getcwd()
SOURCE_TABLES_PATH = os.path.join(PWD, 'sourceTables')
SPARKSQL_TABLES_PATH = os.path.join(PWD, 'sparkTables')
CTL_SELECT_PATH = os.path.join(PWD, 'ctlSelectS')


def init():
    if not os.path.exists(SOURCE_TABLES_PATH):
        print(f"creating dir {SOURCE_TABLES_PATH}")
        os.mkdir(SOURCE_TABLES_PATH)
    if not os.path.exists(SPARKSQL_TABLES_PATH):
        os.mkdir(SPARKSQL_TABLES_PATH)
        print(f"creating dir {SPARKSQL_TABLES_PATH}")
    if not os.path.exists(CTL_SELECT_PATH):
        os.mkdir(CTL_SELECT_PATH)
        print(f"creating dir {CTL_SELECT_PATH}")
