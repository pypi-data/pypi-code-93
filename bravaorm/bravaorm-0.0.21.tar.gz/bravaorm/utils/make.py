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
        if __table_referenced.lower().startswith("fk_"):
            __table_referenced = "_".join(__table_referenced.split("_")[1:])
        count = 0
        while __table_referenced in list:
            count = count + 1
            __table_referenced = "{}{}".format(__table_referenced, count)
        list.append(__table_referenced)
        return __table_referenced

def Make(dir, db_user, db_password, db_host, db_port, db_database, db_ssl=False, db_ssl_ca=None, db_ssl_cert=None, db_ssl_key=None, date_format="%d/%m/%Y %H:%M:%S"):

    _inflector = Inflector(Portugues)

    print("\n [ Python Entity Model ] \n")

    root_path = dir
    model_path = "{}/model/".format(root_path)
    model_lib_path = "{}/model/lib/".format(root_path)

    # create model path
    if not os.path.exists(model_lib_path):
        os.mkdir(model_lib_path)
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

        table_relationships_many = [relationship for relationship in relationships if relationship["referenced_table_name"] == table["TABLE_NAME"]]

        table_relationships_one_to_n = []
        table_relationships_n_to_n = []

        # CHECK AND MAKE LIST FOR MANY TO MANY RELATION
        for many_relation in table_relationships_many:
            table_columns_of_many = [column for column in columns if column["TABLE_NAME"] == many_relation["table_name"]]
            # CHECK IF RELATION IS INTERMEDIATE OF MANY TO MANY
            # IF HAS 2 FIELDS AND ALL FIELDS ARE PRIMARY AND NOT NULL
            if len(table_columns_of_many) == 2 and all([col["COLUMN_KEY"] == 'PRI' and col["IS_NULLABLE"]=="NO" for col in table_columns_of_many]):

                points_of_rel = [relationship for relationship in relationships if relationship["table_name"] == many_relation['table_name']]
                for end_of_rel in points_of_rel:
                    if end_of_rel != many_relation:
                        table_relationships_n_to_n.append({
                                "name": end_of_rel["referenced_table_name"],
                                "reference": many_relation["referenced_column_name"],
                                "table": end_of_rel["referenced_table_name"],
                                "key": end_of_rel["referenced_column_name"],
                                "intermediate": many_relation["table_name"],
                                "ref_key": many_relation["column_name"],
                                "rel_key" : end_of_rel["column_name"],
                                "constraint_name": end_of_rel["constraint_name"]
                            })
            else:
                table_relationships_one_to_n.append(many_relation)

        table_columns = [
            column for column in columns if column["TABLE_NAME"] == table["TABLE_NAME"]]

        path_entitie = "{}/{}.py".format(model_lib_path, classname.lower())
        models.append("from model.lib.{} import {}".format(
            classname.lower(), classname))

        print("\t\t\u2714 Creating Model: {} : {}".format(
            table["TABLE_NAME"], classname))

        with open(path_entitie, "w") as entitie:
            entitie.write("# -*- coding: utf-8 -*-")
            entitie.write("\nfrom bravaorm.entity import *")

            entitie.write(f"\n\nclass {classname}(Entity):")
            entitie.write("\n\n\tdef __init__(cls, **kw):")

            pks = "{" + f"'pk' : {[pk['COLUMN_NAME'] for pk in table_columns if 'COLUMN_KEY' in pk and pk['COLUMN_KEY'] == 'PRI']}" + "}"
            entitie.write(f"\n\n\t\tcls.__metadata__ = {pks}")

            entitie.write("\n\n\t\t# FIELDS".format(pks))
            for table_column in table_columns:

                decorator = "String"
                if "tinyint" in table_column["COLUMN_TYPE"] or "bigint" in table_column["COLUMN_TYPE"] or "int" in table_column["COLUMN_TYPE"]:
                    decorator = "Int"
                elif "decimal" in table_column["COLUMN_TYPE"]:
                    decorator = "Decimal"
                elif "datetime" in table_column["COLUMN_TYPE"]:
                    decorator = "DateTime"
                elif "float" in table_column["COLUMN_TYPE"]:
                    decorator = "Float"

                colum_config = []
                if "datetime" in table_column["COLUMN_TYPE"]:
                    colum_config.append("format='{}'".format(date_format))
                if table_column["COLUMN_KEY"] == 'PRI':
                    colum_config.append("pk=True")
                if table_column["COLUMN_KEY"] == "MUL":
                    colum_config.append("fk=True")
                if table_column["EXTRA"] == 'auto_increment':
                    colum_config.append("auto_increment=True")
                if table_column["IS_NULLABLE"] == "NO":
                    colum_config.append("not_null=True")
                if table_column["CHARACTER_MAXIMUM_LENGTH"] != "NULL" and table_column["CHARACTER_MAXIMUM_LENGTH"] != None:
                    colum_config.append(
                        "max=%s" % table_column["CHARACTER_MAXIMUM_LENGTH"])
                if table_column["NUMERIC_PRECISION"] != None:
                    colum_config.append("precision=%s" %
                                        table_column["NUMERIC_PRECISION"])
                if table_column["NUMERIC_SCALE"] != None:
                    colum_config.append("scale=%s" %
                                        table_column["NUMERIC_SCALE"])

                entitie.write(f"\n\t\tcls.{table_column['COLUMN_NAME']} = {decorator}({', '.join(colum_config)})")


            if len(table_relationships_one_to_one) > 0:
                entitie.write("\n\n\t\t# One-to-One")

            for table_relationship in table_relationships_one_to_one:
                if table_relationship["referenced_table_name"] != table["TABLE_NAME"]:

                    __table_referenced = reference_name(table["TABLE_NAME"], referenced_table, table_relationship["referenced_table_name"], table_relationship["constraint_name"])


                    entitie.write(f"\n\t\tcls.{__table_referenced} = Obj(context=cls, keyname='{__table_referenced}', reference='{table_relationship['column_name']}', name='{_inflector.classify(table_relationship['referenced_table_name'])}', table='{table_relationship['referenced_table_name']}', key='{table_relationship['referenced_column_name']}')")


            if len(table_relationships_one_to_n) > 0:
                entitie.write("\n\n\t\t# One-to-many")

            for table_relationship in table_relationships_one_to_n:

                __table_referenced = reference_name(table["TABLE_NAME"], referenced_table, table_relationship["table_name"], table_relationship["constraint_name"])

                entitie.write(f"\n\t\tcls.{__table_referenced} = ObjList(context=cls, keyname='{__table_referenced}', reference='{table_relationship['referenced_column_name']}',  name='{_inflector.classify(table_relationship['table_name'])}', table='{table_relationship['table_name']}', key='{table_relationship['column_name']}')")

            if len(table_relationships_n_to_n) > 0:
                entitie.write("\n\n\t\t# Many-to-many")

            for table_relationship in table_relationships_n_to_n:

                __table_referenced = reference_name(table["TABLE_NAME"], referenced_table, table_relationship["name"], table_relationship["constraint_name"])

                entitie.write(f"\n\t\tcls.{__table_referenced} = ObjListOfMany(context=cls, keyname='{__table_referenced}', reference='{table_relationship['reference']}', name='{_inflector.classify(table_relationship['name'])}', intermediate='{table_relationship['intermediate']}', ref_key='{table_relationship['ref_key']}', rel_key='{table_relationship['rel_key']}', table='{table_relationship['table']}', key='{table_relationship['key']}')")

            entitie.write("\n\n\t\tsuper().__init__(**kw)")
            entitie.write("\n")

        # WRITE MODEL PY FILE
        path_model = "{}/{}.py".format(model_path, classname.lower())
        if not os.path.exists(path_model):
            with open(path_model, "w") as model_entitie:
                model_entitie.write("# -*- coding: utf-8 -*-")
                model_entitie.write(f"\nfrom bravaorm.entity.datatype import *")
                model_entitie.write(f"\nfrom .lib import {classname}")
                model_entitie.write(f"\n\nclass {classname}({classname}):")
                model_entitie.write("\n\n\tdef __init__(cls, **kw):")
                model_entitie.write(f"\n\t\treturn super({classname}, cls).__init__(**kw)")

    # init model path

    # INICIA PASTA LIB ENTITY __INIT__.PY
    with open("{}/__init__.py".format(model_lib_path), "w") as lib_init_file:
        lib_init_file.write("#-*- coding: utf-8 -*-\n\n")
        lib_init_file.write("\n".join(models))

    print("\n\t\u2714 LIB Init py folder")

    # INICIA PASTA MODEL __INIT__.PY
    with open("{}/__init__.py".format(model_path), "w") as lib_init_file:
        lib_init_file.write("#-*- coding: utf-8 -*-\n\n")
        lib_init_file.write("\n".join(models).replace('model.lib.', 'model.'))

    print("\n\t\u2714 Init py folder")

    print("\n\t\u2714 Done!\n\n")
