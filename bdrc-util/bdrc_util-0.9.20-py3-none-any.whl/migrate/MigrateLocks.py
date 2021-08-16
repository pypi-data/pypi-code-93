"""
Locking utilities
"""
import sys

from DBApps.DbApp import DbApp
import argparse

from config.config import DBConfig


class LockApp(DbApp):
    def __init__(self, db_config: DBConfig):
        super().__init__(db_config)
        pass


lock_operations: [] = ['lock', 'unlock', 'get']


def parse_args() -> argparse.Namespace:
    """
    Set up arg parser
    :rtype: attribute holder
    :return:
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Controls locking and unlocking of migration",
                                                              usage="%(prog)s  work_rid operation")
    parser.add_argument("work_name")
    parser.add_argument("lock_operation", choices=lock_operations)

    return parser.parse_args()


# library API

def lock_work(work_rid: str):
    (DbApp("prod:~/.drsBatch.config")).CallAnySproc("migrate.LockMigration", work_rid, "LOCK")


def unlock_work(work_rid: str):
    (DbApp("prod:~/.drsBatch.config")).CallAnySproc("migrate.LockMigration", work_rid, "UNLOCK")


def is_work_locked(work_rid: str) -> bool:
    lock_app: DbApp = DbApp("prod:~/.drsBatch.config")
    results: [] = lock_app.CallAnySproc("migrate.IsMigrationWorkLocked", work_rid)
    # We want to throw here, no covering up a connection or resource fault
    # means unlocked, anything else means some TBD flavor of lock
    return 0 != results[0][0].get('lock_status')


def migration_lock_control():
    """
    Command line invocation
    :return:
    """
    parsed_args: argparse.Namespace = parse_args()

    if parsed_args.lock_operation == 'lock':
        lock_work(parsed_args.work_name)
    else:
        if parsed_args.lock_operation == 'unlock':
            unlock_work(parsed_args.work_name)
        else:
            if parsed_args.lock_operation == 'get':
                if is_work_locked(parsed_args.work_name):
                    sys.exit(0)
                else:
                    sys.exit(1)


if __name__ == "__main__":
    migration_lock_control()
