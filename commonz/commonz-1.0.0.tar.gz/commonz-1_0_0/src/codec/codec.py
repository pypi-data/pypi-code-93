#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "provide compression or decompression"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2019"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import gzip # compress and decompress just like the GNU programs gzip and gunzip would.
import bz2 # for using the bzip2 compression algorithm.



BZ2_EXT='bz2'



def bz2_compress_file(pathname_source,pathname_destination,memory_size):
	"""compress file with bz2"""
	### compresslevel can be an integer between 1 and 9 
	### 1 produces the least compression
	### and 9 (default) produces the most compression.
	compress_file=bz2.BZ2File(pathname_destination,'w',compresslevel=9)
	datafile=open(pathname_source,'rb')
	
	data=True
	while data :
		data=datafile.read(memory_size)
		compress_file.write(data)
	
	datafile.close()
	compress_file.close()
	
	
def bz2_decompress_file(pathname_source,pathname_destination,memory_size):
	"""uncompress file with bz2"""
	### compresslevel can be an integer between 1 and 9 
	### 1 produces the least compression
	### and 9 (default) produces the most compression.
	compress_file=bz2.BZ2File(pathname_source,'r',compresslevel=9)
	datafile=open(pathname_destination,'wb')

	data=True
	while data :
		data=compress_file.read(memory_size)
		datafile.write(data)

	datafile.close()
	compress_file.close()


