#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module provide condensate calculation for the file system"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import hashlib # Secure hash and digest algorithms.
#import md5 # Deprecated since version 2.5: Use the hashlib module instead.



def get_file_sha(file_path,chunk_size,hexa=True,size=1):
	"""return sha condensate of file"""
	if size==1 :
		hashor = hashlib.sha1()
	elif size==224 :
		hashor = hashlib.sha224()
	elif size==256 :
		hashor = hashlib.sha256()
	elif size==384 :
		hashor = hashlib.sha384()
	elif size==512 :
		hashor = hashlib.sha512()
	else :
		return None

	with open(file_path,'rb') as f:
		data=True
		while data :
			data=f.read(chunk_size)
			hashor.update(data)

	if hexa :
		condensat= hashor.hexdigest()
	else :
		condensat= hashor.digest()

	return condensat


def get_file_md5(file_path,chunk_size,hexa=True):
	"""return md5 condensate of file"""
	hashor = hashlib.md5()
	
	with open(file_path,'rb') as f:
		data=True
		while data :
			data=f.read(chunk_size)
			hashor.update(data)
			
	if hexa :
		condensat= hashor.hexdigest()
	else :
		condensat= hashor.digest()

	return condensat
