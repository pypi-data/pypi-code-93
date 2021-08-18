"""
ssgrab: Download packages from SendSafely
"""

import os
import sys
import re
import textwrap
import base64
import subprocess

import plac
import plac_ini
import json

import sendsafely
from sendsafely import SendSafely, Package
from sendsafely.Progress import Progress
from sendsafely.exceptions import GetPackageInformationFailedException, \
                                  DownloadFileException


class VerbosePrinter:
    def __init__(self, v):
        if v:
            self.print = self.verbose_print
        else:
            self.print = self.null_print

    def verbose_print(self, msg, end='\n'):
        print(msg, file=sys.stderr, end=end)

    def null_print(self, msg, end='\n'):
        pass


class SSGrabProgress(Progress):
    def __init__(self, msg="", verbose=False):
        self.msg = msg
        self.verbose = verbose
        super(SSGrabProgress, self).__init__()

    def update_progress(self, file_id, progress):
        if not self.verbose:
            return

        self.progress = progress

        if progress == '100.0':
            last = '\n'
        else:
            last = ''

        sys.stdout.write(f'\r{self.msg} ({progress}%){last}')
        sys.stdout.flush()


def get_client_secret(link):
   return re.sub(r'^.*keyCode=', '', link)


@plac.annotations(
    verbose=('Verbose output', 'flag', 'v'),
    key=('API key for SendSafely',
             'option', 'k', str, None, 'API_KEY'),
    secret=('API secret for SendSafely',
           'option', 's', str, None, 'SECRET'),
    host=('SendSafely host to connect to, including protocol',
               'option', None, str, None, 'HOST'),
    work_dir=('Working directory in which to store packages. (default: ~/ssgrab/)',
              'option', 'w', str, None, 'WORK_DIR'),
    link=('SendSafely package to download and decrypt',
              'option', 'l', str, None, 'PACKAGE_LINK'),
    postmsg=('Message to follow any verbose output (default: "")',
              'option', None, str, None, 'POSTMSG'),
)
def ssgrab(verbose=False,
           key=None,
           secret=None,
           host=None,
           link=None,
           work_dir=os.path.join(os.path.expanduser('~'), 'ssgrab'),
           postmsg=""):
    "Download packages from SendSafely."

    vp = VerbosePrinter(verbose)
    ss_files = []

    ## Normalize all of the given paths to absolute paths
    work_dir = os.path.abspath(work_dir)

    ## Check for and create working directory
    if not os.path.isdir(work_dir):
        os.makedirs(work_dir)

    # Configure the SendSafely client
    ss = SendSafely(host, key, secret)

    try:
        # Use the provided link to get the attributes of the package
        pkg_info = ss.get_package_information_from_link(link)
    except GetPackageInformationFailedException as err:
        print(f' {err}', file=sys.stderr)
        return []

    # Use the package info together with the keyCode in the link to prepare
    # package variables that will configure the Package object
    pkg_vars = {
      "packageId"    : pkg_info["packageId"],
      "packageCode"  : pkg_info["packageCode"],
      "clientSecret" : get_client_secret(link),
      "serverSecret" : pkg_info["serverSecret"],
    }

    vp.print(f' Downloading SendSafely package {pkg_info["packageId"]}{postmsg}')

    # Initialize a package, passing the instantiated SendSafely client and all
    # of the objects to refer to an existing package that can be retrieved
    package = Package(ss, package_variables=pkg_vars)

    # A package can contain multiple files
    for f in pkg_info["files"]:
        name = f['fileName']
        if os.path.isfile(os.path.join(work_dir, name)):
            vp.print(f'  {name} already present')
            continue

        try:
            p = SSGrabProgress(f'  {name}', verbose)

            # Go and actually get the file and decrypt it in the destination dir
            package.download_and_decrypt_file(f["fileId"],
                    download_directory=work_dir, progress_instance=p)

            ss_files.append(name)
        except DownloadFileException as err:
            print(f' {err}')

    return ss_files


def main(argv=None):
    plac_ini.call(ssgrab)
