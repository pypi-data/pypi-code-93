#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module provide support for temporary files and directories"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import tempfile #for creating and handling temporary files and folders
import os 
from os import path



def get_secure_directory():
	"""get a temporary secure sub directory"""
	temp_dir = tempfile.mkdtemp(suffix='',prefix='')
	return temp_dir


def get_secure_file(ext='',temp_dir=None):
	"""get a temporary secure file"""
	if ext :
		ext= os.extsep+ext
	pathname= tempfile.mkstemp(dir=temp_dir,prefix='',suffix=ext)[1]
	return pathname


def get_named_file(name,ext='',sub_dir=''):
	"""get a named temporary file"""
	if ext :
		name+=os.extsep+ext
	temp_dir = tempfile.gettempdir()
	temp_path= path.join( temp_dir ,sub_dir, name )
	if path.exists(temp_path) :
		raise FileExistsError(temp_path)
	else :
		return temp_path


