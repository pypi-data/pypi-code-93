import logging
import os
from os import walk
from pathlib import Path

from django.core.management import BaseCommand
from isc_common.ssh.ssh_client import SSH_Client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str)
        # parser.add_argument('--message', type=str)

    def handle(self, *args, **options):
        SSH_HOST = '192.168.0.108'
        SSH_HOST = '176.107.243.22'
        SSH_PORT = 22
        SSH_PORT = 20101
        SSH_USER = 'lfl-db'
        SSH_PASSWORD = 'lfl-db'

        c_dumps_path = 'C:\dumps'

        c_files = []
        for (dirpath, dirnames, filenames) in list(walk(c_dumps_path)):
            for filename in filenames:
                full_path_source = f'{dirpath}{os.sep}{filename}'

                stat_source = Path(full_path_source).stat()
                st_mtime = stat_source.st_mtime
                c_files.append((full_path_source, st_mtime))

        c_files.sort(key=lambda x: x[1], reverse=True)
        file, _ = c_files[0]

        SSH_CLIENT = SSH_Client(hostname=SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, port=SSH_PORT)
        # SSH_CLIENT.put(remotepath='/home/lfl-db/tmp/check_inet.sh', localpath='/home/ayudin/check_inet.sh')
        _, only_file = os.path.split(file)
        print('start coping')
        SSH_CLIENT.put(remotepath=f'/home/lfl-db/tmp/{only_file}', localpath=file)
        print('Done.')
