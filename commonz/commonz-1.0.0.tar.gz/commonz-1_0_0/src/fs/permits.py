#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module concern file system permissions for users and others"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import stat
import os
import grp
import pwd
import shutil



### access modes index
READ=0
WRITE=1
EXECUTE=2



def get_owner(pathname):
	"""return file or directory owner name"""
	info=os.lstat(pathname)
	uid=info.st_uid
	user=pwd.getpwuid(uid)
	user_name=user.pw_name
	return user_name

def get_group(pathname):
	"""return file or directory group name"""
	info=os.lstat(pathname)
	gid=info.st_gid
	group=grp.getgrgid(gid)
	group_name=group.gr_name
	return group_name


def set_owner(pathname,owner_name):
	"""Change the owner for the given file or directory"""
	#user=pwd.getpwnam(owner_name)
	#uid = user.pw_uid
	#os.lchown(pathname, uid, -1)#To leave one of the ids unchanged set it to -1.This function will not follow symbolic links.
	shutil.chown(path, user=owner_name)

def set_group(pathname,group_name):
	"""Change the group for the given file or directory"""
	#group=grp.getgrnam(group_name)
	#gid = group.gr_gid
	#os.lchown(pathname, -1, gid)#To leave one of the ids unchanged, set it to -1. This function will not follow symbolic links.
	shutil.chown(path, group=group_name)


def get_owner_permits(pathname):
	"""returns file or directory owner rights"""
	info=os.lstat(pathname)
	mode = info[stat.ST_MODE]
	r=bool(mode&stat.S_IRUSR)
	w=bool(mode&stat.S_IWUSR)
	x=bool(mode&stat.S_IXUSR)
	return (r,w,x)

def get_group_permits(pathname):
	"""returns file or directory group rights"""
	info=os.lstat(pathname)
	mode = info[stat.ST_MODE]
	r=bool(mode&stat.S_IRGRP)
	w=bool(mode&stat.S_IWGRP)
	x=bool(mode&stat.S_IXGRP)
	return (r,w,x)

def get_other_permits(pathname):
	"""returns file or directory other rights"""
	info=os.lstat(pathname)
	mode = info[stat.ST_MODE]
	r=bool(mode&stat.S_IROTH)
	w=bool(mode&stat.S_IWOTH)
	x=bool(mode&stat.S_IXOTH)
	return (r,w,x)


def set_owner_permits(pathname,permits):
	"""set owner permissions for the given pathname"""
	mode = 0
	if permits[READ] :
		mode |= stat.S_IRUSR
	if permits[WRITE] :
		mode |= stat.S_IWUSR
	if permits[EXECUTE] :
		mode |= stat.S_IXUSR
	os.chmod(pathname,mode)
	
def set_group_permits(pathname,permits):
	"""set group permissions for the given pathname"""
	mode = 0
	if permits[READ] :
		mode |= stat.S_IRGRP
	if permits[WRITE] :
		mode |= stat.S_IWGRP
	if permits[EXECUTE] :
		mode |= stat.S_IXGRP
	os.chmod(pathname,mode)
	
def set_other_permits(pathname,permits):
	"""set others permissions for the given pathname"""
	mode = 0
	if permits[READ] :
		mode |= stat.S_IROTH
	if permits[WRITE] :
		mode |= stat.S_IWOTH
	if permits[EXECUTE] :
		mode |= stat.S_IXOTH
	os.chmod(pathname,mode)
	
	
