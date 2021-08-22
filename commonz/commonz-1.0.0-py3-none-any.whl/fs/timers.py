#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module provide information about file system timestamps"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
from datetime import datetime,timezone
#import tzlocal #This Python module returns a tzinfo object with the local timezone information 

import os
from os import path
#import stat



### If True, calls to stat() return floats,if False stat returns ints. 
#os.stat_float_times(False)



def get_change_time(pathname):
	"""return the number of seconds since the UTC epoch of the last meta data change on Unix or creation on Windows"""
	#info=os.lstat(pathname)
	#chg_time = info[stat.ST_CTIME]
	#chg_time = int(info.st_ctime)# give the symlink change time ignoring their target
	chg_time = path.getctime(pathname)
	return chg_time

def get_modification_time(pathname):
	"""return the number of seconds since the UTC epoch of the last modification time"""
	#info=os.lstat(pathname)
	#modif_time = info[stat.ST_MTIME]
	modif_time = path.getmtime(pathname)# not give the symlink mtime but the target mtime
	return modif_time

def get_access_time(pathname):
	"""return the number of seconds since the UTC epoch of the last access time"""
	#info=os.lstat(pathname)
	#acess_time = info[stat.ST_ATIME]
	acess_time = path.getatime(pathname)
	return acess_time


#def set_change_time(pathname,creation_date):
#	"""set the number of seconds since the UTC epoch for the last meta data change on Unix"""
#	### not relevant for Unix systems
#	pass

def set_modification_time(pathname,modification_date):
	"""set the number of seconds since the UTC epoch for the last modification"""
	access_time = path.getatime(pathname)
	os.utime(pathname,(access_time,modification_date)) # take a tuple of form (atime, mtime)

def set_access_time(pathname,access_date):
	"""set the number of seconds since the UTC epoch for the last access"""
	modif_time = path.getmtime(pathname)
	os.utime(pathname,(access_date,modif_time))# # take a tuple of form (atime, mtime)


def convert_time(timestamp,time_zone=True):
	"""convert any epoch timestamp into local or UTC date time"""
	if time_zone :
		tz=None # use local time zone
	else :
		tz=timezone.utc # use utc(gmt) 
	return datetime.fromtimestamp(timestamp,tz)# return <class 'datetime.datetime'>
	
	
