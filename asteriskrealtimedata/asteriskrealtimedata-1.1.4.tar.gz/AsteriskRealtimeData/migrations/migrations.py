import os
from pathlib import Path
import runpy
from datetime import datetime
from sys import path


class ProcessMigrations:
    def __init__(self) -> None:
        self.migration_path = os.path.dirname(os.path.abspath(__file__))
        self.migration_filename = "processed_migrations.list"
        self.migration_path_filename = f"{self.migration_path}/{self.migration_filename}"

    def process_migrations_file(self):
        for filename in os.listdir(self.migration_path):
            if self.filter_migration_file(filename):
                clean_filename = filename.replace(".py", "")
                if self.first_execution(filename):
                    runpy.run_module(f"AsteriskRealtimeData.migrations.{clean_filename}")
                    self.mark_processed(filename)

    def filter_migration_file(self, file_name: str):
        forbidden = ["__init__.py", "migrations.py", f"{self.migration_filename}"]
        return file_name not in forbidden

    def first_execution(self, migration_name: str):
        processed = False
        exists_migrations = Path(self.migration_path_filename).exists()
        if exists_migrations:
            position_in_file = open(f"{self.migration_path_filename}", "r").read().find(f"{migration_name}")
            processed = position_in_file >= 0
        return not processed

    def mark_processed(self, filename: str):
        open(f"{self.migration_path_filename}", "a").write(f"{filename} {datetime.now()}\n")


if __name__ == "__main__":
    ProcessMigrations().process_migrations_file()
