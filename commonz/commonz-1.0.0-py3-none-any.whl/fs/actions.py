#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module provide file system modifications actions"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.1.1"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import os
from os import path
import shutil #High-level files operations, including copying.
#import pathlib
#import tarfile  # manipulation  of tar archive



def move_into(pathname):
	"""set the working directory"""
	os.chdir(pathname)



### FILES


def create_file(pathname):
	"""create a file at the given path"""
	open(pathname,'a').close() # 'a' create a file without truncating it, in case it exists
	

def copy_file(source_pathname,new_pathname):
	"""make copy of file"""
	if path.lexists(new_pathname) :
		raise FileExistsError(new_pathname)
	else :
		### All the shutil copy function requestexisting directories for the new_path
		pathname=path.dirname(new_pathname)
		os.makedirs(pathname,exist_ok=True)# no fail If directory already exists

		### If new_path target a directory, the source_path file will be copied into,
		### If follow_symlinks is true and source_path is a symbolic link, the referenced file will be copied.
		### If new_path is an already existing file, then it will be replaced
		#shutil.copy(source_path,new_path,follow_symlinks=False)
		
		### shutil.copy2 is identical to copy() except attempting to preserve Timestamps.
		### But modification/creation timestamps should be when the copy is made.
		#shutil.copy2(source_path,new_path)
		
		### for shutil.copyfile() the new_path must be a complete file pathname
		### look shutil.copy() for a copy that accepts directory as new_path.
		### If follow_symlinks is false and source_path is a symbolic link, a new symbolic link will be created.
		### If new_path is an already existing file, then it will be replaced
		shutil.copyfile(source_pathname,new_pathname,follow_symlinks=False)
		
		
def empty_file(pathname):
	"""erase file contents,(file size will be zero)"""
	os.truncate(pathname,0)


def delete_file(pathname):
	"""remove a file"""
	os.remove(pathname)# If path is a directory IsADirectoryError is raised.



### DIRECTORIES


def create_directory(pathname):
	"""create directory at the given path"""
	### will create any intermediate directories if necessary
	os.makedirs(pathname,exist_ok=True)# no fail If directory already exists


def copy_directory(source_pathname,new_pathname):
	"""make directories copy"""
	### If symlinks is true, symbolic links in the source tree are copied as symbolic links in the new_path tree.
	### raise FileExistsError if new_path is already an existing file or a directory
	### can create the missing directories to create the new_path
	shutil.copytree(source_pathname,new_pathname,symlinks=True,copy_function=shutil.copy)# dirs_exist_ok python3.8
	
	
def empty_directory(pathname):
	"""delete directory contents"""
	for name in os.listdir(pathname):
		sub_pathname = path.join(pathname,name)
		if path.isdir(sub_pathname):
			shutil.rmtree(sub_pathname,ignore_errors=False)#errors resulting from failed removals will be raised.
		else :
			os.remove(sub_pathname)# If path is a directory IsADirectoryError is raised.


def delete_directory(pathname):
	"""remove a directory and all his contents."""
	#os.remove(directory_path) # If path is a directory IsADirectoryError is raised.
	#os.rmdir(directory_path)# FileNotFoundError or OSError is raised If directory not exist or not empty
	shutil.rmtree(pathname,ignore_errors=False)# if 'ignore_errors=True' errors resulting from failed removals will be ignored.
	


### GENERIC (not specific)
	
	
def link(link_pathname,target_pathname):
	"""Create a link pointing to target_pathname at the given link_pathname.
	Target_pathname must be relative to link_pathname"""
	os.symlink(target_pathname,link_pathname)


def copy(source_pathname,new_pathname):
	"""make files or directories copies"""
	if path.isdir(source_pathname):
		copy_directory(source_pathname,new_pathname)
	else:
		copy_file(source_pathname,new_pathname)
		
		
def rename(pathname,old_name,new_name):
	"""change the name of files or directories"""
	old_pathname= path.join(pathname,old_name)
	new_pathname= path.join(pathname,new_name)
	if path.lexists(new_pathname) :# lexists returns True even for broken symbolic links
		### Raise error if a file or directory already exist at the pathname.
		raise FileExistsError(new_pathname)# There is no specific error code for already existing directory.
	else :
		#os.renames(old_pathname,new_pathname)# Works like rename() but create any intermediate directories
		os.rename(old_pathname,new_pathname)#If old and new pathnames are existing files, new_pathnames is replaced
		
		
def move(old_pathname,new_pathname):
	"""change path and name of the given file or directory"""
	if path.lexists(new_pathname):# lexists returns True even for broken symbolic links
		raise FileExistsError(new_pathname)# There is no specific error code for already existing directory
	else :
		#shutil.move(old_pathname,new_pathname)# fail to create intermediate directories

		#os.rename(old_pathname,new_pathname)#If old and new pathnames are existing files, new_pathnames is replaced

		os.renames(old_pathname,new_pathname)# Works like rename() but create any intermediate directories
		### if file->file eraze destination file
		### if file->directory fail with IsADirectoryError
		### if directory->directory work if destination is an empty folder
		### if directory->file fail with NotADirectoryError
	
	
def delete(pathname):
	"""delete the given file or directory"""
	if path.isdir(pathname):
		delete_directory(pathname)
	else:
		delete_file(pathname)
	
