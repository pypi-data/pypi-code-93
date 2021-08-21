from pathlib import Path

from myvault.statics.formatted_enum import FormattedEnum

SQL_DIR = Path(__file__).parent.parent / "sql"


class Query(FormattedEnum):
    CREATE_TABLE = SQL_DIR / "create_table.sql"
    INSERT_SECRET = SQL_DIR / "insert_secret.sql"
    UPDATE_SECRET = SQL_DIR / "update_secret.sql"
    SELECT_ALL = SQL_DIR / "select_all.sql"
    SELECT_FOLDER_NAME = SQL_DIR / "select_folder_name.sql"
    SELECT_SECRET = SQL_DIR / "select_secret.sql"
    DELETE_SECRET = SQL_DIR / "delete_secret.sql"

    def formatted(self, **kwargs) -> str:
        with open(file=self.value, mode="r") as file:
            return file.read().format(**kwargs)
