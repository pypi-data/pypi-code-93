
import os
import shutil
import datetime
import tempfile
import pathlib
import os.path
from updrytwist import config
import asyncio


# exit codes
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class SimpleFileRotator:

    def __init__ ( self, directory : str, nVersions : int = 10, configuration : {} = None ):

        self.nVersions = config.dictread( configuration, "NbrVersionsToKeep", nVersions )
        self.directory = config.dictread( configuration, "Directory",         directory )

    async def openFile ( self, fileName : str ):
        # Open up a new file for writing.  Rotate old versions of the file, up to the maximum count.
        await self.rotateVersions( fileName )
        return open( fileName, "w")

    def fullName ( self, fileBase : str, number : int ) -> str:
        return os.path.join( self.directory, fileBase + ".{:03d}".format( number ))

    async def rotateVersions ( self, fileName : str ) -> None:
        baseName = pathlib.Path(fileName).stem
        for version in range(self.nVersions - 1, 0, -1):
            await asyncio.sleep(0)
            fullPath = self.fullName( baseName, version )
            if os.path.exists(fullPath):
                if version == self.nVersions - 1:
                    os.remove( fullPath )
                else:
                    os.rename( fullPath, self.fullName( baseName, version+1 ))
        fullPath = os.path.join( self.directory, fileName )
        if os.path.exists(fullPath):
            os.rename( fullPath, self.fullName( baseName, 1 ))


class DirectoryFileRotator:

    date_formats = {
        'hourly': '%Y-%m-%dT%H',
        'daily': '%Y-%m-%d',
        'weekly': '%Y-W%W',
        'monthly': '%Y-%m',
    }

    def __init__(self, dest_dir, hours, days, weeks, months, hard_link=False,
                 remove=False, verbose=False):
        self.keep_count = {
            'hourly': hours,
            'daily': days,
            'weekly': weeks,
            'monthly': months,
        }

        self.dest_dir = dest_dir
        self.hard_link = hard_link
        self.remove = remove
        self.verbose = verbose

        self.files = []

    def add_files(self, files):
        self.files.extend(files)

    def __verb(self, msg):
        if self.verbose:
            print(msg)

    @staticmethod
    def copy(src, dest):
        shutil.copy2(src, dest)
        stat = os.stat(src)
        if hasattr(os, 'chown'):
            os.chown(dest, stat.st_uid, stat.st_gid)

    def __rotate_file(self, filename, dry_run=False):
        basename = os.path.basename(filename)

        temp_file = os.path.join(self.__temp_dir, basename)
        self.__verb("Copying {} to {}".format(basename, temp_file))
        if not dry_run:
            self.copy(filename, temp_file)

        for rotate_class, prefix_format in iter(self.date_formats.items()):
            keep_count = self.keep_count[rotate_class]
            dir_path = os.path.join(self.dest_dir, rotate_class,
                                    datetime.datetime.now().strftime(prefix_format))
            dest_path = os.path.join(dir_path, basename)

            if keep_count > 0 and not os.path.isdir(dir_path):
                self.__verb("mkdir {}".format(dir_path))
                if not dry_run:
                    os.mkdir(dir_path)

            if keep_count <= 0:
                self.__verb("{} limit {}, not creating file {}".format(
                        rotate_class, keep_count, dest_path))
            elif os.path.exists(dest_path):
                self.__verb("{} exists, skipping".format(dest_path))
            else:
                if self.hard_link:
                    self.__verb("Linking {}".format(dest_path))
                    if not dry_run:
                        os.link(temp_file, dest_path)
                else:
                    self.__verb("Copying {}".format(dest_path))
                    if not dry_run:
                        self.copy(temp_file, dest_path)

        if self.hard_link:
            self.__verb("Unlinking {}".format(temp_file))
            if not dry_run:
                os.unlink(temp_file)

        if self.remove:
            self.__verb("Removing source {}".format(filename))
            if not dry_run:
                os.unlink(filename)

    def __trim(self, dry_run=False):
        for rotate_class, keep_count in iter(self.keep_count.items()):
            dir_path = os.path.join(self.dest_dir, rotate_class)
            if not os.path.exists(dir_path):
                existing_count = 0
                existing = []
            else:
                existing = sorted(os.listdir(dir_path))
                existing_count = len(existing)

            self.__verb("{}/{} {} directories".format(
                    existing_count, keep_count, rotate_class))
            if existing_count > keep_count:
                self.__verb("Trimming to {}".format(keep_count))
                for directory in existing[:-keep_count]:
                    directory = os.path.join(dir_path, directory)
                    self.__verb("Removing {}".format(directory))
                    if not dry_run:
                        shutil.rmtree(directory)

    def rotate(self, dry_run=False):
        result = EXIT_SUCCESS
        if dry_run:
            print("Performing a dry run - no changes will be made.")

        if not os.path.isdir(self.dest_dir):
            self.__verb("mkdir -p {}".format(self.dest_dir))
            if not dry_run:
                os.makedirs(self.dest_dir)

        for rotate_class, count in iter(self.keep_count.items()):
            if count > 0:
                dir_path = os.path.join(self.dest_dir, rotate_class)
                if not os.path.isdir(dir_path):
                    self.__verb("mkdir {}".format(dir_path))
                    if not dry_run:
                        os.mkdir("{}".format(dir_path))

        if dry_run:
            self.__temp_dir = "/tmp"
        else:
            self.__temp_dir = tempfile.mkdtemp()
        self.__verb("Working directory {}".format(self.__temp_dir))

        for in_file in self.files:
            file_path = os.path.abspath(in_file)
            if os.path.exists(file_path):
                self.__verb("rotating {}".format(file_path))
                self.__rotate_file(file_path, dry_run)

        self.__trim(dry_run)

        if not dry_run:
            self.__verb("Removing working directory {}".format(self.__temp_dir))
            shutil.rmtree(self.__temp_dir)

        return result
