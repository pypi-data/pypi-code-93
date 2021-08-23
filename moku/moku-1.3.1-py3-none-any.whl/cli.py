#!/usr/bin/env python
import hashlib
import os
import sys
from argparse import ArgumentParser

import requests
from moku import __version__, DATA_PATH

from .finder import Finder
from .version import compat_fw

MOKU_DATA_URL = f'http://updates.liquidinstruments.com/static/mokudata-{compat_fw[0]}.tar.gz'

parser = ArgumentParser()
subparsers = parser.add_subparsers(title="action", dest='action',
                                   description="Action to take")
subparsers.required = True


def list_mokus(args):
    results = Finder().find_all(timeout=args.wait,
                                filter=lambda x: x.hwver == 4.0)
    spacing = "{: <7} {: <6} {: <20}"

    print(spacing.format('Serial', 'FW', 'IP'))
    print("-" * (7 + 6 + 20 + 4))

    results.sort(key=lambda a: a.serial)

    for m in results:
        print(spacing.format(m.serial, m.fwver, m.ipv4_addr))


parser_list = subparsers.add_parser('list', help="List Moku's on the network.")
parser_list.add_argument('--wait', '-w',
                         type=float,
                         help="Browse for n seconds before concluding results",
                         default=5.0)
parser_list.set_defaults(func=list_mokus)


def download(args):
    local_data_path = os.path.join(DATA_PATH, f'mokudata-{compat_fw[0]}.tar.gz')
    try:
        r = requests.get(MOKU_DATA_URL.replace('tar.gz', 'md5'))
        r.raise_for_status()  # Checks for any HTTP errors
        remote_hash = r.text.split(' ')[0]
        if os.path.exists(local_data_path):
            local_hash = hashlib.md5(open(local_data_path, 'rb').read()).hexdigest()
            if not args.force and remote_hash == local_hash:
                print("Instruments already up to date.")
                return
        else:
            os.makedirs(DATA_PATH, exist_ok=True)
        print('Downloading latest instruments...')
        with requests.get(MOKU_DATA_URL, stream=True) as r:
            r.raise_for_status()  # Check for any HTTP errors
            length = int(r.headers['content-length'])
            recvd = 0
            with open(local_data_path, 'wb+') as f:
                for chunk in r.iter_content(chunk_size=400000):
                    f.write(chunk)
                    recvd = recvd + len(chunk)
                    sys.stdout.write("\r[%-30s] %3d%%" %
                                     ('#' * int(30.0 * recvd / length),
                                      (100.0 * recvd / length)))
                    sys.stdout.flush()
                sys.stdout.write('\r[%-30s] Done!\n' % ('#' * 30))

            with open(local_data_path, 'rb') as f:
                print('Verifying download..')
                if hashlib.md5(f.read()).hexdigest() == remote_hash:
                    print('Download complete')
                else:
                    print('Unable to verify download, please try again')
    except requests.HTTPError as e:
        print("ERROR: Unable to retrieve updates from server.\n%s" % str(e))
        return
    except Exception as e:
        print("ERROR: Unexpected error.\n%s" % str(e))


parser_dl = subparsers.add_parser('download', help="Download instrument bitstreams.")
parser_dl.add_argument('--force', action='store_true')
parser_dl.set_defaults(func=download)


def main():
    print("Moku Client Version %s" % __version__)
    args = parser.parse_args()
    args.func(args)


# Compatible with direct run and distutils binary packaging
if __name__ == '__main__':
    main()
