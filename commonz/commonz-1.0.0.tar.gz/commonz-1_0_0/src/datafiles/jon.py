#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



### JSON = JavaScript Object Notation



__doc__ = "JSON files reading and writing."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020-06-20"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



import json



def get_keys(json_file):
	"""return dictionary from JSON file"""
	with open(json_file,'r') as f :
		return json.load(f)


def write_file(db,output_file):
	"""Write JSON file from the given dictionary"""
	with open(output_file,'w') as of :
		jd=json.dumps(db)
		of.write( jd )

