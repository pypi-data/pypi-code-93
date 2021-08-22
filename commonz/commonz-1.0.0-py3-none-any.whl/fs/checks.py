#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module allow to check and get info about the file system"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import stat # module defines constants and functions for interpreting the results of os stat
import os
from os import path
#import pathlib # filesystem paths with semantics appropriate for different operating systems
#import urllib # modules for working with URLs
import shutil
import filecmp # this module defines functions to compare files and directories,

import mimetypes	#giving files MIME types.


### types constants for file system items
TYPE_DIRECTORY='directory'
TYPE_SYMBOLIC_LINK ='symbolic_link'
TYPE_FILE='file'
TYPE_UNKNOW='unknow'
TYPE_SPECIAL_CHARACTER_DEVICE='Character_device'
TYPE_BLOK_DEVICE='Block_device'
TYPE_FIFO='fifo'
TYPE_SOCKET='socket'

### platform constants names
PLATFORM_LINUX='linux'
PLATFORM_WINDOWS='win'
PLATFORM_UNKNOW='unknow'



def pathname(pathname):
	"""check if the given path and name point to an existing file or directory"""
	return path.exists(pathname)

def directory_pathname(pathname):
	"""check if the given path and name point to an existing directory"""
	return path.isdir(pathname) 

def file_pathname(pathname):
	"""check if the given path and name point to an existing file"""
	return path.isfile(pathname)

def link_pathname(pathname):
	"""check if the given path and name point to an existing link"""
	return path.islink(pathname)


def file_size(pathname):
	"""for given file path gives the size in bytes."""
	#info=os.lstat(pathname)
	#size = info[stat.ST_SIZE]
	size = path.getsize(pathname)	
	### if pahtname is a link return 4096 for a pointed directory or the size of the pointed file
	### raise error if the file does not exist or is inaccessible.
	return size

	
def get_mimetype(pathname):
	"""for the given file path return the mime type"""
	return mimetypes.guess_type(pathname,strict=True)#strict means registered with IANA.

def get_type(pathname):
	"""for the given path name return the type"""
	info=os.lstat(pathname)
	mode = info[stat.ST_MODE]
	if stat.S_ISLNK(mode) :
		return TYPE_SYMBOLIC_LINK
	elif stat.S_ISDIR(mode):
		return TYPE_DIRECTORY
	elif stat.S_ISCHR(mode) :
		return TYPE_SPECIAL_CHARACTER_DEVICE
	elif stat.S_ISBLK(mode) :
		return TYPE_BLOK_DEVICE
	elif stat.S_ISREG(mode):
		return TYPE_FILE
	elif stat.S_ISFIFO(mode) :
		return TYPE_FIFO
	elif stat.S_ISSOCK(mode) :
		return TYPE_SOCKET
	else :
		return TYPE_UNKNOW


def same_files(f1,f2):
	"""check if the 2 files are the same,(compare byte by byte the contents)"""
	### If shallow is true, files with identical os.stat() are equal.
	### Otherwise, the contents of files are compared.
	return filecmp.cmp(f1, f2, shallow=False)


def disk_usage(pathname):
	"""Return disk usage statistics for the given path"""
	### Return tuple with the attributes total,used,free in bytes.
	### usage(total=118013599744, used=63686647808, free=48352747520)
	return shutil.disk_usage(pathname)


def hardlink_qantum(pathname):
	"""return the number of harlinks made for the given pathname"""
	info=os.lstat(pathname)
	qantum = info[stat.ST_NLINK]
	return qantum


def platform_os():
	"""return the name of the current used operating system platform"""
	### can be used to detect the operating systems: os.name,os.uname(),sys.platform,platform.platform(),platform.system(),platform.system_alias(),platform.uname()
	### the operating system information should be also in the env variables, but its not certain
	if sys.platform.startswith(PLATFORM_LINUX):
		return PLATFORM_LINUX
	elif platform.startswith(PLATFORM_WINDOWS):
		return PLATFORM_WINDOWS
	else :
		return PLATFORM_UNKNOW


