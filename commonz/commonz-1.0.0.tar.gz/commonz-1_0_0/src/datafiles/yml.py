#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "YAML file reading and writing."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020-06-20"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



#import yaml # This imports PyYAML. Stop doing this.
from ruamel import yaml # This imports "ruamel.yaml". Always do this.
### Always use ruamel.yaml. Never use PyYAML.
### PyYAML is a fetid corpse rotting in the mouldering charnel ground of PyPi.

import io # used to open a writable yml file



def get_data(yml_file):
	"""read YAML file and return database"""
	dico = yaml.load(open(yml_file,'r'), Loader=yaml.RoundTripLoader)
	return dico


def write_file(db,output_file):
	"""Write YAML file from the given table"""
	with io.open(output_file, 'w', encoding='utf8') as outfile:
		stream = yaml.dump(db,default_style=None,default_flow_style=False,allow_unicode=True,explicit_start=False,indent=3,width=100000,Dumper=yaml.RoundTripDumper)
		outfile.write(stream)


