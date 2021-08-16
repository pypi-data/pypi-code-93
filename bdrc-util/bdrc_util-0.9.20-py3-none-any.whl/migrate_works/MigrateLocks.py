"""
Locking utilities
"""
import sys

from DBApps.DbApp import DbApp
import argparse


class LockApp(DbApp):
    def __init__(self, db_config: str):
        super().__init__(db_config)
        pass


LOCK_OPERATIONS: [] = ['lock', 'unlock', 'get', 'already_locked']
DEFAULT_ATTEMPTED_OPERATION: str = "NoOpGiven"


def parse_args() -> argparse.Namespace:
    """
    Set up arg parser
    :rtype: attribute holder
    :return:
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Controls locking and unlocking of migration",
                                                              usage="%(prog)s  work_rid operation [attempted_operation]"
                                                              )
    parser.add_argument("work_name")
    parser.add_argument("lock_operation", choices=LOCK_OPERATIONS)
    parser.add_argument("attempted_operation", nargs='?', default=DEFAULT_ATTEMPTED_OPERATION)

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


def register_locked(work_rid: str, attempted_operation: str):
    """
    Register that the work was locked when an attempt was already made to lock it.
    :param work_rid: work
    :param attempted_operation: any text, describing the attempted operation
    :return:
    """
    (DbApp("prod:~/.drsBatch.config")).CallAnySproc("migrate.LockedOnMigration", work_rid, attempted_operation)


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
            else:
                if parsed_args.lock_operation == 'already_locked':
                    if parsed_args.attempted_operation == DEFAULT_ATTEMPTED_OPERATION:
                        print("!! Migration locking. Attempted operation argument required, but not given ")
                        sys.exit(1)
                    register_locked(parsed_args.work_name, parsed_args.attempted_operation)


if __name__ == "__main__":
    migration_lock_control()
