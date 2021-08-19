"""
Locking utilities
"""
from DBApps.DbApp import DbApp
import argparse

from config.config import DBConfig


class LockApp(DbApp):
    def __init__(self, db_config: DBConfig):
        super().__init__(db_config)
        pass


lock_operations: [] =  ['lock', 'unlock', 'get']
def parse_args() -> argparse.Namespace:
    """
    Set up arg parser
    :rtype: attribute holder
    :return:
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Controls locking and unlocking of migration",
                                                              usage="%(prog) [-v] work_rid ")
    parser.add_argument("work_name", required=True)
    parser.add_argument("lock_operation", choices=lock_operations, required=True)

    return parser.parse_args()

def do_lock(db: DbApp, work_rid: str):
    db.CallAnySproc("migrate.lock")

def migration_lock():
    """
    Entry point to set a works lock state
    :return:
    """
    parsed_args: argparse.Namespace = parse_args()

    # TODO: Make some default in the base dbApp parser
    lock_app: DbApp = DbApp(DBConfig("prod:~/.drsBatch.config"))

    if parsed_args.lock_operation == 'lock':
        do_lock(lock_app, parsed_args.work_name)




