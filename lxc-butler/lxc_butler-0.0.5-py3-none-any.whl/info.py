from os import readlink
from os.path import expanduser, relpath
from getpass import getuser

# package info
__version__ = '0.0.5'
__author__ = 'Kobus van Schoor'
__author_email__ = 'v.schoor.kobus@gmail.com'
__url__ = 'https://github.com/kobus-v-schoor/lxc-butler'
__license__ = 'MIT License'

# user info
username = getuser()
home = expanduser('~')
timezone = relpath(readlink('/etc/localtime'), '/usr/share/zoneinfo')

# set the default distro and release
distro = 'debian'
release = 'bullseye'
arch = 'amd64'
