#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "This module concern links chain."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
#__copyright__ = "Copyright 2000, The X Project"
__date__ = "2009-01"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



class Link:
	"""a link of chain"""
	def __init__(self,data):
		"""data is the value stored by the link"""
		self.data=data
		self.previous=None
		self.next=None

	def delete(self):
		"""delete link"""
		#print("del")
		if self.previous!=None :
			self.previous.set_next(self.next)
		if self.next!=None :
			self.next.set_previous(self.previous)
		self=None#

	def set_next(self,next=None):
		"""set the next link"""
		self.next=next
	def get_next(self):
		"""return the next link"""
		return self.next
	
	def set_previous(self,previous=None):
		"""set the previous link"""
		self.previous=previous
	def get_previous(self):
		"""return the previous link"""
		return self.previous
	
	def get_data(self):
		"""return the data stored by the link"""
		return self.data
		
def build_chain(items):
	start=Link(items[0])
	old=start
	for i in items[1:] :
		new=Link(i)
		old.set_next(new)
		new.set_previous(old)
		old=new
	return start
	
