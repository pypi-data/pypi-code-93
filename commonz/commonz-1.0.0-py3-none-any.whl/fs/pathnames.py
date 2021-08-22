#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module concern path and names of all directories and files on the system"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import os
from os import path #for handling directory files and their path
import pathlib # use for .ext
import stat # use for hardlinks
#import re #Regular expression operations
#import fnmatch # support for Unix shell-style wildcards, which are not the same as regular expressions
#import glob # finds all the pathnames matching a specified pattern according to the rules used by the Unix shell 



def get_common_path(path_list):
	"""returns part of the path common to all the paths in the list"""
	return path.commonpath(path_list)

def get_relativ_path(from_pathname,to_pathname):
	"""return a relative pathname"""
	return path.relpath(to_pathname,from_pathname)

def get_real_path(pathname):
	"""returns the given path removing any ambiguity"""
	### realpath() use direct path instead symbolic links
	### abspath() no relative path, all start from root /
	### expanduser() replace home symbols by the user path
	### normpath() collapse relative redundant path, A/foo/../B become A/B
	return path.realpath(path.abspath(path.expanduser(path.normpath(pathname))))


def get_path(pathname):
	"""extract and return the first part of the given pathname"""
	return path.dirname(pathname)

def get_name(pathname):
	"""extract and return the last part of the given pathname"""
	return path.basename(pathname)

def join_pathname(dirs,name):
	"""from directories and name parts return a pathname"""
	return path.join(dirs,name)


def get_base_name(pathname):
	"""from a complete file name return the first part, without any ext"""
	name = pathlib.Path(pathname)
	while name.suffixes :
		name= pathlib.Path(name.stem)
	return name.stem

def join_base_name_ext(base_name,ext_list):
	"""returns a path made up of the base name and one or more extensions"""
	return os.extsep.join([base_name]+ext_list)

def get_name_ext(pathname):
	"""from a complete file name return the last part composed of one or more ext"""
	ext_list=[]
	for ext in pathlib.Path(pathname).suffixes :
		ext_list.append( ext.strip(os.extsep) )
	return ext_list


def get_directory_content(search_path,includ_files=True,includ_directories=True,fullpath=True):
	"""returns the list of the contents of the given directory"""	
	pathnames=[]
	for name in os.listdir(search_path) :
		pathname= path.join(search_path,name)
		#print(pathname)#
		if (path.isdir(pathname) and includ_directories) or (path.isfile(pathname) and includ_files) :
			if fullpath :
				pathnames.append(pathname)
			else :
				pathnames.append(name)
	return pathnames

def get_recursive_content(search_path,includ_files=True,includ_directories=True,fullpath=True):
	"""returns the list of the contents of the given directory and its subdirectories"""
	pathnames_list=[]
	for root, dirs, files in os.walk(search_path,topdown=False):
		if not includ_files :
			files=[]
		if not includ_directories :
			dirs=[]
		for name in dirs+files :
			pathname= path.join(root,name)# root contain the all path.
			if not fullpath :
				pathname= path.relpath(pathname,search_path)
			pathnames_list.append(pathname)
	return pathnames_list


def filter_pathname(pathname,includ=[],exclud=[],default=True):
	""" 
	returns True if path in exclud list
	returns False if path in includ list
	or return default valu
	"""
	while pathname!='/' :
		if pathname in includ :
			return False
		elif pathname in exclud :
			return True
		else :
			#print(pathname)#
			pathname=path.dirname(pathname)
	return default

def filter_ext(fullname,ext_list):
	"""
	returns True if path name ext is in ext list
	returns False if path name ext is Not in ext list
	"""
	ext_list= [ e.lower() for e in ext_list] # lower all ext in the given list
	ext_list= [ e.strip(os.extsep) for e in ext_list] # remove all ext separators in the given list
	#print(ext_list)#
	
	name_ext= pathlib.Path(fullname).suffixes
	#name_ext= path.splitext(fullname)[1] # only split 1 ext,
	#print(name_ext)#
	for ext in name_ext :
		ext=ext.lower()
		ext=ext.strip(os.extsep)
		#print(ext)#
		if ext in ext_list :
			return True
	return False

def filter_html_folders(pathname):
	"""
	returns True if pathname is an html directory
	otherwise returns False
	"""
	if path.isdir(pathname) :
		if pathname.endswith("_fichiers") or pathname.endswith("_files") :
			return True
	return False


def get_mount_path(pathname):
	"""returns the file system mount point for the given pathname"""
	pathname= path.abspath(pathname)
	while not path.ismount(pathname):
		pathname= path.dirname(pathname)
	return pathname


def get_link_target(link_path):
	"""Returns a string representing the pathname to which the given symbolic link points."""
	link_target=os.readlink(link_path)
	return link_target

def get_hardlinks(file_path):
	"""for the given file returns the list of hard links paths"""
	### please make me better
	hardlinks=[]
	info=os.lstat(file_path)
	qantum = info[stat.ST_NLINK]
	if qantum>1 :
		inode = info[stat.ST_INO]
		mount_path=get_mount_path(file_path)
		#print("mount point:",mount_path)#
		pathname_list=get_recursive_content(mount_path,includ_files=True,includ_directories=False)
		for pathname in pathname_list :
			#print(pathname)#
			if path.isfile(pathname) and not pathname==file_path :
				info=os.lstat(pathname)
				if info[stat.ST_INO]==inode :
					hardlinks.append(pathname)
	return hardlinks


def get_counted_name(dir_path,prefix='',sufix='',hexa=False):
	"""gives one available hexadecimal name"""
	if hexa :
		conv='x' #Hex format, lower case
	else :
		conv='d' #Decimal format
		
	number=1
	while True :
		numfix=format(number,conv)
		name=prefix+numfix+sufix
		pathname=path.join(dir_path,name)
		if not path.exists(pathname) :
			return name
		else :
			number+=1
