import os
from argparse import ArgumentParser, Namespace
import logging
import datetime

from playvision.storage.swift import SwiftSelectelStorage
from playvision.database.couchbase import CouchbaseBackup

COUCH_PASS = os.environ['COUCH_PASS']
SWIFT_PASS = os.environ['SWIFT_PASS']

logging.basicConfig(level=logging.INFO)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--couch-user', required=True, type=str, help='Couchbase user')
    parser.add_argument('--couch-url', required=True, type=str, help='Couchbase URL')
    parser.add_argument('--swift-user', required=True, type=str, help='Selectel Cloud Storage user')
    parser.add_argument('--sel-id', required=True, type=str, help='Selectel accound id: 12345')
    parser.add_argument('--sel-project-id', required=True, type=str, help='Selectel project id')
    parser.add_argument('--bucket-name', required=True, type=str, help='Swift bucket name')
    parser.add_argument('--backup-name', required=True, type=str, help='Backup name prefix')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    cb = CouchbaseBackup(args.couch_user, COUCH_PASS, args.couch_url)
    backupfile = cb.make_backup_archive()
    today = datetime.date.today().isoformat()
    storage = SwiftSelectelStorage(args.swift_user, SWIFT_PASS, args.sel_id, args.sel_project_id)
    storage.upload(args.bucket_name, backupfile, f'{today}-{args.backup_name}', 1024*1024*1024)
    os.unlink(backupfile)
