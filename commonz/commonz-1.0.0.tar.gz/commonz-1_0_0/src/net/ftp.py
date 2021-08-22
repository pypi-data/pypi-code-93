#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this module is for connexions with the FTP"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020-6-17"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import all required modules
import ftplib

import os # for local pathname check and making directories



### ftp functions

class Ftp:
	"""for connexions with the FTP host"""
	def __init__(self,host='',port=None,user='',password=''):
		"""need host name or ip address"""
		if port :
			self.connection = ftplib.FTP(user=user,passwd=password,source_address=(host,port))
		else :
			self.connection = ftplib.FTP(host=host,user=user,passwd=password)


	def get_current_location(self):
		"""Return the pathname of the current directory on the server."""
		return self.connection.pwd()
		
		
	def move_into(self,pathname):
		"""change the current distant directory location"""
		self.connection.cwd(pathname)
		
		
	def get_content(self,includ_files=True,includ_directories=True):
		"""list files directories in the current distant location"""
		content_list=[]
		#content = self.connection.retrlines('LIST',callback=None)# Retrieve file directory listing in ASCII.
		#content = self.connection.nlst( )# If server supports it, mlsd() offers better API
		#content = self.connection.dir( )# If server supports it, mlsd() offers better API
		content= self.connection.mlsd(facts=["type"])# can raise error with some ftp servers
		for o in content :
			name=o[0]
			metadata=o[1]
			tip=metadata["type"]
			if (tip=='dir' and includ_directories) or (tip=='file' and includ_files) :
				content_list.append(name)
		return content_list


	def get_file_size(self,filename):
		"""get the size in bytes of distant file"""
		size= self.connection.size(filename)
		return size
	
	
	def download_file(self,filename,local_path,overwrite=False):
		"""download a distant file by FTP"""
		if os.path.lexists(local_path) and overwrite==False :
			raise FileExistsError(local_path)
		else :
			directory=os.path.dirname(local_path)
			os.makedirs(directory,exist_ok=True)
			
			with open(local_path, 'wb') as f:
				self.connection.retrbinary('RETR '+filename,f.write)
			
			
	def close(self):
		"""close the connexion"""
		self.connection.quit()
		
		
