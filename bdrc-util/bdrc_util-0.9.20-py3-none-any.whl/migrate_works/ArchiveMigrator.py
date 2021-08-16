import datetime
import os
import shutil

import sys
import traceback
from pathlib import Path

# This import is more tricky than you'd like. If you simply from DbApps import DbApp, you are just importing the
# module, not the base class DbApps.DbApp.DbApp see
# https://stackoverflow.com/questions/47228290/python-subclass-typeerror-takes-at-most-2-arguments-3-given-while-it
# -should
from DBAppParser import DbAppParser, str2date
from DBApps.DbApp import DbApp
from archive_ops.Resolvers import Resolvers
from archive_ops.shell_ws import get_mappings
from migrate_works.MigrateLocks import lock_work, unlock_work, is_work_locked, register_locked
from util_lib import AOLogger

from util_lib.GetFromBUDA import get_disk_volumes_in_work


class ArchiveMigrator(DbApp):
    """
    Records the migration of a volume
    """

    def __init__(self, db_config: str, input_list_path: str, source_parent: str, dest_parent: str,
                 migration_date: datetime,
                 log: AOLogger) -> None:
        """
        Constructor
        :param db_config: string describing section and config file location
        :param source_parent: parent directory containing works to migrate
        :param dest_parent: root from which
        ("works_source_parent", help='Parent folder of works to be migrated')
        self._parser.add_argument("dest_parent", help='Parent folder of archive pools')
        self._parser.add_argument("migration_date", nargs='?',
        :type db_config: object
        """
        super().__init__(db_config)
        if input_list_path is not None:
            self.input_list = Path(input_list_path)
        else:
            self.input_list = None
        self.source_parent: Path = Path(source_parent).expanduser().resolve()
        self.dest_parent: Path = Path(dest_parent).expanduser().resolve()
        self.migration_date = migration_date
        self.log = log

        self.parent_must_exist(self.source_parent)


    def migrate_archive(self) -> None:
        """
        Migrate an archive, log migration status of each volume in the archive
        :return:
        """
        # Get the volumes in the archive
        # TODO: This could be problematic - it does the whole root
        # for source_work in os.scandir(self.source_parent):
        #
        #     if source_work.is_dir():
        #         target_dir = get_mappings(str(self.dest_parent), source_work.name, Resolvers.DEFAULT)
        #         self.lock_migration(source_work.name)
        #         self.migrate_work(source_work.name, source_work.path, target_dir)
        #         self.unlock_migration(source_work.name)
        # noinspection PyTypeChecker
        for source_work_path in next_in_list(self.source_parent, self.input_list):
            source_name = source_work_path.name
            
            if not source_work_path.exists():
                self.log_not_exists(source_work_path)
                continue
            target_dir = get_mappings(str(self.dest_parent), source_name, Resolvers.DEFAULT)

            if is_work_locked(source_name):
                self.log.warn(f"{source_name} locked, skipping.")
                register_locked(source_name, 'migrate')
                continue
            lock_work(source_name)
            try:
                self.migrate_work(str(source_work_path), target_dir)
            finally:
                unlock_work(source_name)

    def migrate_work(self, source_tree_path_str: str, target_path_str: str) -> None:
        """
        Migrates one work's listed volumes, with logging and error checking
        :param source_tree_path_str: fq source directory (/foo/W12345) Path object
        :param target_path_str: fq volume destination directory (/bar/W12345)
        :return:
        """
        target_path: Path = Path(target_path_str)
        target_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        work_name = target_path.name
        # noinspection PyBroadException
        try:
            tick: datetime.datetime = datetime.datetime.now()
            shutil.copytree(source_tree_path_str, target_path_str)
            work_facts: () = get_work_facts(target_path_str)
            tock: datetime.datetime = datetime.datetime.now()
            self.log_migration(work_name, target_path, max(1, (tock - tick).seconds), work_facts)

        except FileExistsError:
            self.log_exists(work_name, target_path)
        except Exception:
            exc = sys.exc_info()
            self.log.error(f"error {exc[1]} migrating {source_tree_path_str} to {target_path_str}\n"
                           f" {traceback.print_tb(exc[2], limit=5)}")
        finally:
            pass

    def log_exists(self, work_name: str, target_path: Path) -> None:
        """
        Report on the image groups found on disk
        :param work_name: work_RID
        :param target_path: fq parent of image group parents
        """
        work_volumes: [] = get_work_volume_path_names(work_name)
        for parent in ('archive', 'images'):
            for volume_label in work_volumes:
                work_volume_path = Path(target_path, parent, volume_label)
                if work_volume_path.exists():
                    self.register_already_exists(work_name, volume_label, str(work_volume_path))

    def log_migration(self, work_name: str, target_path: Path, elapsed_sec: int, facts: ()) -> None:
        """
        Loops over a named set of parents and reports on the image groups found
        :param work_name: work_RID
        :param target_path: fq parent of image group parents
        :param elapsed_sec: how long this took
        :param facts: fact tuple:  [0] = total size, [1] file count
        """

        self.CallAnySproc("drs.AddWorkFacts", work_name, facts[0], facts[1])

        for volume_label in get_work_volume_path_names(work_name):
            in_archive: bool = Path(target_path, 'archive', volume_label).exists()
            in_images: bool = Path(target_path, 'images', volume_label).exists()

            # AddMigration call sequence: AddMigration( IN migration_date datetime,
            #                                           IN volume_label varchar(45),
            #                                           IN Work_rid varchar(72),
            #                                           IN migration_path varchar(45),
            #                                           IN in_archive tinyint(1),
            #                                           IN in_images tinyint(1))
            self.log.info(f"Migrating {work_name} / {volume_label} has_arc:{in_archive} has_images:{in_images}")
            self.CallAnySproc("migrate.LogMigration", self.migration_date, volume_label, work_name,
                              str(target_path), in_archive, in_images)
        try:
            self.log.info(f"Stats:{work_name}: size:{facts[0]}: file_count:{facts[1]}: "
                          f"rate:{'{0:0.2f}: / sec'.format(facts[0] / max(1, elapsed_sec))}")
        finally:
            pass  # dontcare on fail

    def parent_must_exist(self, tested: Path) -> None:
        if not tested.exists():
            self.log.error(f"{str(tested)} not found. ")
            raise FileNotFoundError(str(tested))

    def register_already_exists(self, work_name: str, volume_label: str, existing_path: str) -> None:
        """
        Log that a destination exists
        :param work_name:  work_RID
        :param volume_label:  Image group/volume name
        :param existing_path:  existing migration destination
        """
        # LogMigrationExists call sequence: LogMigrationExists(
        #                                           IN work_dest_path varchar(255),
        #                                           IN Work_rid varchar(45),
        #                                           IN volume_label varchar(45))

        self.log.warn(f" Work {work_name} volume {volume_label} found at {existing_path}")
        self.CallAnySproc("migrate.LogMigrationExists", existing_path, work_name, volume_label)

    def log_not_exists(self, source_work_path: Path):
        self.log.warn(f" Work {source_work_path.name} not found at {source_work_path.parent}")
        self.CallAnySproc("migrate.LogWorkNotOnDisk", str(source_work_path), source_work_path.name)


def get_work_volume_path_names(work_name) -> []:
    """
    :returns the work volume names according to the repository
    :param work_name:
    :return:
    """
    return ['{}-{}'.format(work_name, x.get('vol_label')) for x in get_disk_volumes_in_work(work_name)]


def get_work_facts(a_path: str) -> (int, int):
    """
    Returns the sum of all file sizes and file count in a path
    64 bit python platforms (2 and 3)report sys.maxsize as
    9,223,372,036,854,775,807  or 9 exaBytes.
    """
    size: int = 0
    _count: int = 0
    from os.path import join, getsize
    for root, dirs, files in os.walk(a_path):
        size += sum(getsize(join(root, name)) for name in files)
        _count += len(files)
    return size, _count


def next_in_list(parent: Path, input_file: Path) -> Path:
    """
    Generator function to either iterate over every object in a path, or over every line in a file, prefixed with the
    path :rtype: Path :param parent: Pathlike object - should have been fully qualified already :param input_file: if
    not None, a file containing a list of directory names :return: next in the iteration
    """
    if input_file is None:
        with os.scandir(parent) as it:
            for entry in it:
                if entry.is_dir():
                    yield Path(entry.path)
    else:
        for w_ in open(input_file, 'r'):
            yield Path(parent, w_.rstrip())


class ArchiveMigrationParser(DbAppParser):
    """
    Parser for the Archive Migration class
    Returns a structure containing fields:
    .drsDbConfig: str (from base class DBAppArgs
    .works_source_parent: str: parent folder of works to migrate. Everything in this folder is migrated
    .dest_parent: str : root from which the bucket destination will be derived
    .migration_date: object:  date of migration
    """

    def __init__(self, description: str, usage: str):
        """
        Constructor. Sets up the arguments for
        """
        super().__init__(description, usage)
        self._parser.add_argument("-l", "--log-level", dest='log_level', action='store',
                                  choices=['info', 'warning', 'error', 'debug', 'critical'], default='info',
                                  help="choice values are from python logging module")

        self._parser.add_argument("-i", "--input_list", required=False,
                                  help="optional file list of directories relative to works_source_parent, instead of "
                                       "everything in works source parent")

        self._parser.add_argument("works_source_parent", help='Parent folder of works to be migrated')
        self._parser.add_argument("dest_parent", help='Prefix of archive destination paths - relative or fully '
                                                      'qualified ')
        self._parser.add_argument("migration_date", nargs='?',
                                  help='date of Migration. Defaults to date this call was made.',
                                  default=datetime.datetime.now(), type=str2date)
