# -*- coding: utf-8 -*-

import sys
import os
import re

import mysql.connector as mariadb
from bravaorm.utils.inflector import Inflector, Portugues

def reference_name(table, list, name, fk_name):
    __table_referenced = name
    if not __table_referenced in list and __table_referenced != table:
        list.append(__table_referenced)
        return __table_referenced
    else:
        __table_referenced = fk_name
        count = 0
        while __table_referenced in list:
            count = count + 1
            __table_referenced = "{}{}".format(__table_referenced, count)
        list.append(__table_referenced)
        return __table_referenced

def Angular(dir, db_user, db_password, db_host, db_port, db_database, db_ssl=False, db_ssl_ca=None, db_ssl_cert=None, db_ssl_key=None, date_format="%d/%m/%Y %H:%M:%S"):

    _inflector = Inflector(Portugues)

    print("\n [ Angular Model Class] \n")

    model_path = dir

    # create model path
    if not os.path.exists(model_path):
        os.mkdir(model_path)
        print("\t\u2714 Creating Model Folder on Project")
    else:
        print("\t\u2714 Model Folder Exists")

    print("\t\u2714 Connecting Database...")

    # SQL EXECUTA SQL QUERY
    if not db_ssl:
        db = mariadb.connect(user=db_user, password=db_password,
                             host=db_host, port=db_port, database=db_database)
    else:
        db = mariadb.connect(user=db_user, password=db_password, host=db_host, port=db_port,
                             database=db_database, ssl_ca=db_ssl_ca, ssl_cert=db_ssl_cert, ssl_key=db_ssl_key)

    cursor = db.cursor(dictionary=True)

    print("\t\u2714 Fetching Tables")

    # REFLECTION TABELAS DO PROJETO
    cursor.execute("SELECT TABLE_NAME FROM information_schema.tables where table_schema='{database}' ORDER BY TABLE_NAME ASC".format(
        database=db_database))
    tables = cursor.fetchall()

    cursor.execute("SELECT DISTINCT information_schema.key_column_usage.constraint_name, information_schema.key_column_usage.table_name, information_schema.key_column_usage.column_name, information_schema.key_column_usage.referenced_table_name, information_schema.key_column_usage.referenced_column_name FROM information_schema.key_column_usage, information_schema.tables AS tables, information_schema.tables AS referenced_tables WHERE information_schema.key_column_usage.table_schema='{database}' AND tables.table_name = information_schema.key_column_usage.table_name AND referenced_tables.table_name = information_schema.key_column_usage.referenced_table_name AND information_schema.key_column_usage.referenced_table_name IS NOT NULL  ORDER BY TABLE_NAME ASC".format(
        database=db_database))
    relationships = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM information_schema.columns where table_schema='{0}' ORDER BY TABLE_NAME ASC, ORDINAL_POSITION ASC".format(db_database))
    columns = cursor.fetchall()

    print("\t\u2714 Create Entities: \n")

    models = []

    for table in tables:

        referenced_table = []

        classname = _inflector.classify(table["TABLE_NAME"])

        table_relationships_one_to_one = [
            relationship for relationship in relationships if relationship["table_name"] == table["TABLE_NAME"]]

        table_relationships_one_to_n = [
            relationship for relationship in relationships if relationship["referenced_table_name"] == table["TABLE_NAME"]]

        table_relationships_n_to_n = []

        # CHECK AND MAKE LIST FOR MANY TO MANY RELATION
        for to_many_relation in table_relationships_one_to_n:
            table_columns_to_many = [column for column in columns if column["TABLE_NAME"] == to_many_relation["table_name"]]
            # CHECK IF HAS 2 FIELDS AND ALL FIELDS ARE PRIMARY AND NOT NULL
            if len(table_columns_to_many) == 2 and all([col["COLUMN_KEY"] == 'PRI' and col["IS_NULLABLE"]=="NO" for col in table_columns_to_many]):
                table_relationships_to_many = [relationship for relationship in relationships if relationship["table_name"] == to_many_relation["table_name"] and relationship["referenced_table_name"] != table["TABLE_NAME"]][0]
                table_relationships_n_to_n.append({"name": table_relationships_to_many["referenced_table_name"], "table": table_relationships_to_many["referenced_table_name"], "intermediate": to_many_relation["table_name"], "key": to_many_relation["column_name"], "reference": to_many_relation["referenced_column_name"], "inter_key" : table_relationships_to_many["column_name"], "end_key": table_relationships_to_many["referenced_column_name"], "constraint_name": table_relationships_to_many["constraint_name"]})


        table_columns = [
            column for column in columns if column["TABLE_NAME"] == table["TABLE_NAME"]]

        path_entitie = "{}/{}.ts".format(model_path, classname.lower())
        models.append(f"export * from './{classname.lower()}';")

        print("\t\t\u2714 Creating Model: {} : {}".format(table["TABLE_NAME"], classname))

        with open(path_entitie, "w") as entitie:

            tb_imported = []
            cl_imported = []
            for table_relationship in table_relationships_one_to_one:
                if table_relationship["referenced_table_name"] != table["TABLE_NAME"] and not table_relationship["referenced_table_name"] in tb_imported:
                    cl_imported.append(_inflector.classify(table_relationship["referenced_table_name"]))
                    tb_imported.append(table_relationship["referenced_table_name"])

            for table_relationship in table_relationships_one_to_n:
                if table_relationship["table_name"] != table["TABLE_NAME"] and not table_relationship["table_name"] in tb_imported:
                    cl_imported.append(_inflector.classify(table_relationship["table_name"]))
                    tb_imported.append(table_relationship["table_name"])

            entitie.write("import {\n\t" + ",\n\t".join(cl_imported)+ " \n} from '.';")


            entitie.write(f"\n\nexport class " + classname + " { ")
            entitie.write("\n\n\t__object__ = '{}'".format(classname))
            metadada = {}

            for table_column in table_columns:

                field_type = "string"
                meta_type = "string"
                if "tinyint" in table_column["COLUMN_TYPE"]:
                    field_type = "number"
                    meta_type = "tinyint"
                elif "bigint" in table_column["COLUMN_TYPE"]:
                    field_type = "number"
                    meta_type = "bigint"
                elif "int" in table_column["COLUMN_TYPE"]:
                    field_type = "number"
                    meta_type = "int"
                elif "decimal" in table_column["COLUMN_TYPE"]:
                    field_type = "number"
                    meta_type = "decimal"
                elif "datetime" in table_column["COLUMN_TYPE"]:
                    field_type = "Date"
                    meta_type = "date"
                elif "float" in table_column["COLUMN_TYPE"]:
                    field_type = "number"
                    meta_type = "float"

                precision = table_column["NUMERIC_PRECISION"] if table_column["NUMERIC_PRECISION"] else 0
                scale = table_column["NUMERIC_SCALE"] if table_column["NUMERIC_SCALE"] else 0
                max = table_column["CHARACTER_MAXIMUM_LENGTH"] if table_column["CHARACTER_MAXIMUM_LENGTH"] else 0

                metadada[table_column['COLUMN_NAME']] = { 'title' : table_column['COLUMN_COMMENT'], 'type': meta_type, 'precision': precision, 'scale': scale, 'max': max}
                entitie.write(f"\n\t{table_column['COLUMN_NAME']}: {field_type};")

            if len(table_relationships_one_to_one) > 0:
                entitie.write("\n\n\t // One-to-One")

            for table_relationship in table_relationships_one_to_one:
                if table_relationship["referenced_table_name"] != table["TABLE_NAME"]:

                    __table_referenced = reference_name(table["TABLE_NAME"], referenced_table, table_relationship["referenced_table_name"], table_relationship["constraint_name"])

                    _rel_class = _inflector.classify(table_relationship["referenced_table_name"])
                    entitie.write(f"\n\t{__table_referenced}: {_rel_class};")

            if len(table_relationships_one_to_n) > 0:
                entitie.write("\n\n\t // One-to-many")

            for table_relationship in table_relationships_one_to_n:
                if table_relationship["table_name"] != table["TABLE_NAME"]:

                    __table_referenced = reference_name(table["TABLE_NAME"], referenced_table, table_relationship["table_name"], table_relationship["constraint_name"])

                    _rel_class = _inflector.classify(table_relationship["table_name"])
                    entitie.write(f"\n\t{__table_referenced}: {_rel_class}[];")


            # entitie.write("\n\n\t__metadata__ = {}".format())
            # metadada = base64.b64encode(str(metadada).encode()).decode('utf-8');
            entitie.write(f"\n\n\t__metadata__ = {metadada}")

            entitie.write("\n}")

    # init model path

    # INICIA PASTA LIB ENTITY __INIT__.PY
    with open("{}/index.ts".format(model_path), "w") as lib_init_file:
        lib_init_file.write("\n".join(models))

    print("\n\t\u2714 Done!\n\n")
