import os
import sqlite3
from pathlib import Path

from appdirs import user_data_dir


def get_db_path() -> str:
    data_directory = user_data_dir(appname="kolo", appauthor="kolo")

    storage_path = os.path.join(data_directory, "storage")
    Path(storage_path).mkdir(parents=True, exist_ok=True)

    custom_database_name = os.environ.get("KOLO_PROJECT_NAME")

    if custom_database_name is not None:
        database_name = custom_database_name.lower()
    else:
        current_folder_name = os.path.basename(os.getcwd()).lower()
        database_name = current_folder_name

    return os.path.join(storage_path, f"{database_name}.sqlite3")


def create_invocations_table(db_path) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS invocations (
        id text PRIMARY KEY NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        data text NOT NULL
    );
    """

    create_timestamp_index_query = """
        CREATE INDEX IF NOT EXISTS
        idx_invocations_created_at
        ON invocations (created_at);
        """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(create_table_query)
    cursor.execute(create_timestamp_index_query)
    cursor.close()
    conn.close()


def setup_db() -> str:
    db_path = get_db_path()
    create_invocations_table(db_path)
    return db_path


def save_invocation_in_sqlite(
    db_path: str, invocation_id: str, json_string: str
) -> None:
    insert_sql = """
        INSERT OR IGNORE INTO invocations(id, data)
        VALUES(?,?)
        """

    # We can't reuse a connection
    # because we're in a new thread
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(insert_sql, (invocation_id, json_string))
    conn.commit()
    cursor.close()
    conn.close()
