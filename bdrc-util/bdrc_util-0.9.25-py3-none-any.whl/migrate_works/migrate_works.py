"""
Put_volume_data:
Register the move of a piece of data
"""
import os
from pathlib import Path

from DBAppParser import DbArgNamespace
from util_lib import AOLogger

from migrate_works.ArchiveMigrator import ArchiveMigrator, ArchiveMigrationParser


def migrate_works_shell():
    mp: DbArgNamespace = ArchiveMigrationParser(description="Records the migration of archives to the new scheme",
                                                usage=" works_source_parent dest_parent").parsedArgs
    aol = AOLogger.AOLogger("archive-migrate_works", mp.log_level, Path(os.getcwd()))

    works_source_parent = str(Path(mp.works_source_parent).expanduser().resolve())
    dest_parent = str(Path(mp.dest_parent).expanduser().resolve())

    log_message = f'Migrating {mp.works_source_parent} to {mp.dest_parent} Begin'
    aol.info(log_message)
    abspath = mp.input_list
    if mp.input_list is not None:
        abspath = os.path.abspath(mp.input_list)
    am = ArchiveMigrator(mp.drsDbConfig, abspath, works_source_parent, dest_parent, mp.migration_date, aol)
    am.migrate_archive()
    log_message = f'Migrating {mp.works_source_parent} End'
    aol.info(log_message)


if __name__ == "__main__":
    migrate_works()
