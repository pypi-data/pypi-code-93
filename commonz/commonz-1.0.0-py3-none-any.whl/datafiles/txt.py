#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "Read and Write Lines of Text Files."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2021"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### os.linesep
import os



def read_lines(pathname,comments='',blanks=False):
	"""get the files lines with or without the comments and blanks"""
	lines_list=[]
	with open(pathname,'r') as f:
		### A file is already an iterable full of lines.
		### And it's a smart iterable, reading lines as you need them, with some clever buffering under the covers.
		### .readlines() reads all the file into memory before starting to loop
		for line in f :
			line=line.strip()
			if line=='' and not blanks :
				pass
			elif comments and line.startswith(comments) :
				pass
			else :
				lines_list.append(line)
	return lines_list


def write_file(pathname,lines_list,append=False):
	""" write lines of files on local drive"""
	### os.linesep bug !
	### any '\n' characters written are translated to the system default line separator
	### on Windows writing os.linesep is the same as writing \r\n which contains \n
	### which is translated and result to \r\r\n
	if append :
		f=	 open(pathname,'a')
	else :
		f=	 open(pathname,'w')
	### .writelines() does not add line separators
	for line in lines_list :
		f.write( line+'\n' )
	f.close()
