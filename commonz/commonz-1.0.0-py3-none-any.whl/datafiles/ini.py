#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "INI File Reading and Writing."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2021"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



class Parser:
	def __init__(self, pathname):
		self.parse = {'':{}}
		self.pathname = pathname
	
	def read(self):
		section=''
		with open(self.pathname,'r') as f:
			### A file is already an iterable full of lines.
			### And it's a smart iterable, reading lines as you need them, with some clever buffering under the covers.
			### .readlines() reads all the file into memory before starting to loop
			for line in f :
				line=line.split("#")[0]
				line=line.split(";")[0]
				line=line.strip()
				if line=='' :
					pass
				elif line.startswith('[') and line.endswith(']') :
					section = line.strip("[]")
					self.parse.update({section:{}})
				elif line.find("=") :
					pair = line.split("=")
					key = pair[0].strip()
					value = pair[1].strip()
					self.parse[section].update({key: value})
				else :
					raise EOFError
	
	def get_sections(self):
		return self.parse.keys()
	
	def get_keys(self,section):
		return self.parse[section].keys()
	
	def get_valu(self,section,key):
		return self.parse[section][key]
	
	def set_valu(self,section,key,valu):
		self.parse[section][key]=str(valu)
	
	def add_section(self,section):
		self.parse[section]={}
	
	def add_key(self,section,key):
		self.parse[section][key]=''
		
	def write_file(self,pathname=None):
		if not pathname :
			pathname=self.pathname
		with open(pathname,'w') as f:
			for section in self.parse.keys() :
				f.write( '[{}]\n'.format(section) )
				for key in self.parse[section].keys() :
					valu=self.parse[section][key]
					f.write( '{} = {}\n'.format(key,valu) )
				f.write( '\n' )
