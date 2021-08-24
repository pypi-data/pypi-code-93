import os, sys
import tempfile
import subprocess
import tarfile
import shutil
import logging


class CouchbaseBackup:
    def __init__(self, couch_user, couch_pass, couch_url):
        self.args = [
            'cbbackup',
            '-u', couch_user,
            '-p', couch_pass,
            couch_url
        ]
        self.tempdir = tempfile.mkdtemp()

    def make_backup_archive(self) -> str:
        self._backup()
        fd, tar_fname = tempfile.mkstemp(suffix='.tgz')
        os.close(fd)
        logging.info(f'Compress {self.tempdir} to {tar_fname}')
        with tarfile.open(tar_fname, 'w:gz') as tar:
            tar.add(self.tempdir)
        return tar_fname

    def _backup(self):
        self.args.append(self.tempdir)
        try:
            result = subprocess.run(self.args, check=True)
            logging.info(result)
        except subprocess.CalledProcessError as e:
            logging.error('cant create backup')
            logging.error(e)
            sys.exit(1)

    def __del__(self):
        shutil.rmtree(self.tempdir)
