from django.apps import apps as installed_apps
from django.db import connections, router

from .crypto import Crypto


class Migrator:
    def __init__(self, app, model, field, key=None, tofield=None, idfield="id"):
        self.app = app
        self.model = model.lower()
        self.field = field.lower()
        self.crypto = Crypto(key)
        self.tofield = tofield
        self.idfield = idfield

    def encrypt(self, apps=None, schema_editor=None, offset=0, total=None, limit=1000):
        return self.executor(apps, schema_editor, offset, total, limit, method="encrypt")

    def decrypt(self, apps=None, schema_editor=None, offset=0, total=None, limit=1000):
        return self.executor(apps, schema_editor, offset, total, limit, method="decrypt")

    def copy_to(self, apps=None, schema_editor=None, offset=0, total=None, limit=1000):
        return self.executor(apps, schema_editor, offset, total, limit, method="copy_to")

    def encrypt_to(self, apps=None, schema_editor=None, offset=0, total=None, limit=1000):
        return self.executor(apps, schema_editor, offset, total, limit, method="encrypt_to")

    def decrypt_to(self, apps=None, schema_editor=None, offset=0, total=None, limit=1000):
        return self.executor(apps, schema_editor, offset, total, limit, method="decrypt_to")

    def get_db_parameters(self, apps=None, model=None, schema_editor=None):
        if not apps:
            apps = installed_apps
        if not schema_editor:
            db_alias = router.db_for_write(model=model)
        else:
            db_alias = schema_editor.connection.alias
        db_table = model._meta.db_table if model._meta.db_table else f"{self.app}_{self.model}"
        return db_alias, db_table

    def calculate_total_and_limit(self, model, db_alias, limit, total):
        if limit == -1:
            total = model.objects.using(db_alias).count()
        else:
            if not total:
                last_record = model.objects.using(db_alias).order_by(f"-{self.idfield}").first()
                if last_record:
                    total = getattr(last_record, self.idfield)
                else:
                    total = 0
            if limit > total:
                limit = total
        return limit, total

    def process_cursor(self, cursor, method, value_list):
        value_list = []
        for query in cursor.fetchall():
            if method in ["encrypt", "encrypt_to"]:
                value_list.append([query[0], self.crypto.encrypt(query[1])])
            elif method in ["decrypt", "decrypt_to"]:
                text = self.crypto.decrypt(query[1]) or ""
                value_list.append([query[0], text.replace("'", "''")])
            elif method == "copy_to":
                text = query[1] or ""
                value_list.append([query[0], text.replace("'", "''")])
        return value_list

    def process_value_list(self, db_table, method, value_list):
        execute_sql = ""
        for value in value_list:
            if method in ["encrypt", "decrypt"]:
                if value[1] is None:
                    execute_sql += f"update {db_table} set {self.field}=NULL where {self.idfield}='{value[0]}';"
                else:
                    execute_sql += f"update {db_table} set {self.field}='{value[1]}' where {self.idfield}='{value[0]}';"
            elif method in ["copy_to", "encrypt_to", "decrypt_to"]:
                if value[1] is None:
                    execute_sql += f"update {db_table} set {self.tofield}=NULL where {self.idfield}='{value[0]}';"
                else:
                    execute_sql += (
                        f"update {db_table} set {self.tofield}='{value[1]}' where {self.idfield}='{value[0]}';"
                    )
        return execute_sql

    def executor(self, apps=None, schema_editor=None, offset=0, total=None, limit=1000, method=None):
        if not method:
            return

        model = apps.get_model(self.app, self.model)
        db_alias, db_table = self.get_db_parameters(apps, model, schema_editor)
        limit, total = self.calculate_total_and_limit(model, db_alias, limit, total)

        while offset < total:
            value_list = []
            with connections[db_alias].cursor() as cursor:
                if limit == -1:
                    cursor.execute(f"select {self.idfield}, {self.field} from {db_table};")
                else:
                    cursor.execute(
                        f"select {self.idfield}, {self.field} from {db_table} where {self.idfield}>{offset} "
                        f"order by {self.idfield} limit {limit};"
                    )
                cursor_value_list = self.process_cursor(cursor, method)
                value_list.extend(cursor_value_list)
                execute_sql = self.process_value_list(db_table, method, value_list)
                cursor.execute(execute_sql)
            if value_list:
                if limit == -1:
                    offset = total
                else:
                    offset = value_list[-1][0]
