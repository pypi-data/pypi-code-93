#    Virtual-IPM is a software for simulating IPMs and other related devices.
#    Copyright (C) 2021  The IPMSim collaboration <https://ipmsim.gitlab.io/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import codecs
import os
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    'cst_file',
    help='Filename of the CST file to be converted.'
)
parser.add_argument(
    '--csv-file',
    help='CSV output filename. If not given the csv filename is determined from the cst filename.'
)
parser.add_argument(
    '--overwrite',
    action='store_true',
    help='Use this flag to overwrite an existing CSV file. Otherwise the script will abort.'
)
args = parser.parse_args()


def main():
    if not args.csv_file:
        path, ext = os.path.splitext(args.cst_file)
        csv_file = '{0}.{1}'.format(path, 'csv')
    else:
        csv_file = args.csv_file
    if os.path.exists(csv_file) and not args.overwrite:
        print('Output csv file "%s" already exists. Use --overwrite to replace the file.' % csv_file)
        sys.exit()
    print('Writing output to: ', csv_file)

    with codecs.open(args.cst_file, encoding='ascii') as f_in, \
            codecs.open(csv_file, 'w', encoding='ascii') as f_out:
        header = f_in.readline()
        header = re.sub(r'\s{2,}', r',', header)
        if header.endswith(','):
            header = header[:-1]
        if header.startswith(','):
            header = header[1:]
        f_out.write(header + '\n')
        for entry in f_in:
            entry = entry.strip()
            if not entry or re.match(r'^-+$', entry) is not None:
                continue
            cols = list(filter(
                None,
                entry.split(' ')
            ))
            csv_entry = ','.join(map(str, cols))
            f_out.write(csv_entry + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
