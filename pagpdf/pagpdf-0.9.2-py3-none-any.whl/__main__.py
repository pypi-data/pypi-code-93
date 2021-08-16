#!/usr/bin/python3

# imports

from .__init__ import __doc__ as description, __version__ as version
from sys import argv, exit
from argparse import ArgumentParser as Parser, RawDescriptionHelpFormatter as Formatter
from pdfrw import PdfReader

# classes

class args:
    'container for arguments'
    pass

# main

def pagpdf(argv):
    'print number of PAGes in PDF files'

    # get arguments
    parser = Parser(prog='pagpdf', formatter_class=Formatter, description=description)
    parser.add_argument('-V', '--version', action='version', version=f'pagpdf {version}')
    parser.add_argument('-c', '--csv-header',  action='store_true', help='print CSV header as first line (default: don\'t)')
    parser.add_argument('-n', '--sort-by-pages',  action='store_true', help='sort files by number of pages (default: sort by filename)')
    parser.add_argument('-r', '--reverse',  action='store_true', help='sort files in descending order (default: sort in ascending order)')
    parser.add_argument('-t', '--total-too',  action='store_true', help='print file list and total line (default: print file list)')
    parser.add_argument('-T', '--total-only',  action='store_true', help='print total line only (default: print file list)')
    parser.add_argument('file', nargs='*', help='files to be listed (non-pdf files are silently skipped)')
    parser.parse_args(argv[1:], args)
    args.file = [file for file in args.file if file.endswith('.pdf')]

    # check arguments
    if args.total_too and args.total_only:
        exit('ERROR: you can\'t set both -t/--total-too and -T/--total-only')
        
    # scan files into buffer  
    buffer = []; nfil = 0; ntot = 0
    for file in args.file:
        try:
            npag = len(PdfReader(file).pages)
        except:
            npag = 0
        buffer.append((npag, file))
        nfil += 1
        ntot += npag

    # sort buffer
    if not args.total_only:
        if args.sort_by_pages:
            buffer.sort(reverse=args.reverse)
        else:
            buffer.sort(reverse=args.reverse, key=lambda npag_file: (npag_file[1], npag_file[0]))
    
    # print buffer
    if args.csv_header:
        print(f'NUM\tPAG\tFILE')
    if not args.total_only:
        for jfil, npag_file in enumerate(buffer):
            npag, file = npag_file
            print(f'{jfil + 1}\t{npag}\t{file}')
    if args.total_too or args.total_only:
        print(f'{nfil}\t{ntot}\tTOTAL')
        
def main():
    try:
        pagpdf(argv)
    except KeyboardInterrupt:
        print()

if __name__ == '__main__':
    main()
