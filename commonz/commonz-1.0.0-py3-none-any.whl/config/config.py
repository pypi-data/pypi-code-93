#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "this modul is useful for setting programs at startup, returning the merge of configuration files and command line instructions"
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "v3.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2008/10"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### no LOGS !
### because the logging system is not yet configured at the startup, this module will provide logging parameters.

### no TRANSLATION ! (multilingual, internationalization, localization)
### because the translation must be configured before starting, this module will provide translations parameters.



### import the required modules

import sys # only use for sys.argv and sys.exit

### configargparse is interesting but not yet in default python instalation and not in the Debian distribution
#import configargparse # combin of command line args, config files, hard-coded defaults, environment variables and in someothers
import configparser # config files parser
import argparse # command line parser
#import anyconfig # python-anyconfig load and dump conf files in various formats, with features such as contents merge, templates, query, schema validation and generation support.

import string # manipulation of character strings
import shlex # Split strings using shell-like syntax, ignoring comment in the string .
from distutils import util # strtobool(string) convert	true y yes true on 1		false n no f off 0	Raises ValueError if anything else



CFG_ERROR_MSG1="config files error: missing section [{}]"
CFG_ERROR_MSG2="config files error: missing '{}' in section [{}]"
CFG_ERROR_MSG3="config files error: invalid value for '{}' in section [{}]"
CMD_INDEX_SEPARATOR='='
CMD_CAT_ARG="ARG" # section for the given args 
CMD_PIPE_ARG='-'# use for a specifie input or output args by pipe
#CMD_VERSION_MSG="show program version" #prefer to restrict cmd help to how to use
DESCRIPTION=None # use by the comandline --help for additional information,should keep this text common generic



class Config :
	"""for the merge of command lines and configuration files"""
	def __init__(self):
		self.cfg=Config_File()
		self.cmd=Command_line()

	def read_configfile(self,pathname):
		"""parse the primary default initfiles"""
		self.cfg.read_configfile(pathname)
		
	def read_optional_configfiles(self,init_file_list):
		"""parse the optional initfiles, listed by priority order"""
		self.cfg.read_optional_configfiles(init_file_list)

	def add_arg(self,arg,tip,qantum,help):
		"""request for one or more values ​​in the command line
		if qantum=0 many values or at least one will be attributed"""
		self.cmd.add_arg(arg,tip,qantum,help)
		
	def add_choice(self,shortflag,longflag,tip,qantum,choices,help,category,name):
		"""specifies in config files or in the command line some chosen values
				if qantum=0 many values or at least one will be attributed"""
		self.cmd.add_choice(shortflag,longflag,tip,qantum,choices,help,category,name)
		self.cfg.add_format(category,name,tip,qantum,choices)
		
	def add_positive_flag(self,shortflag,longflag,help,category,name):
		"""specifies in the configuration files or in the command line an option which will be equal to True"""
		self.cmd.add_positive_flag(shortflag,longflag,help,category,name)
		self.cfg.add_format(category,name,bool,1,None)
		
	def add_negative_flag(self,shortflag,longflag,help,category,name):
		"""specifies in the configuration files or in the command line an option which will be equal to False"""
		self.cmd.add_negative_flag(shortflag,longflag,help,category,name)
		self.cfg.add_format(category,name,bool,1,None)
		
	def add_valu(self,shortflag,longflag,tip,qantum,help,symbols,category,name):
		"""for these otions in the configuration files or in the command line some values will be stored
		if qantum=0 many values or at least one will be attributed"""
		self.cmd.add_valu(shortflag,longflag,tip,qantum,help,symbols,category,name)
		self.cfg.add_format(category,name,tip,qantum,None)

	def get(self):
		"""merge and return the configuration files and the command line parameters"""

		setting=self.cfg.get()
		#print(cfg)
		mode=self.cmd.get()
		#print(cmd)

		for category in mode.keys() :
			if not category in setting :
				setting[category]={}
			setting[category].update(mode[category])

		return setting



class Config_File :
	"""init configuration files parser"""
	def __init__(self):
		self.parser = configparser.ConfigParser(strict=True,interpolation=None,delimiters=('=',':'),comment_prefixes=('#',';'),inline_comment_prefixes=('#',';'),allow_no_value=False,empty_lines_in_values=False )
		self.format={}

	def read_configfile(self,pathname):
		"""parse the primary default initfiles"""
		cfg_file=open(pathname,'r')
		self.parser.read_file(cfg_file)
		cfg_file.close()

	def read_optional_configfiles(self,init_file_list):
		"""parse the optional initfiles, listed by priority order"""
		self.parser.read(init_file_list)

	def add_format(self,category,name,tip=str,qantum=1,choices=None):
		"""specifies in the init files a config value format."""
		if not category in self.format :
			self.format[category]={}
		self.format[category][name]={"qantum":qantum,"choices":choices,"tip":tip}

	def get(self):
		"""return result of the parsed configuration files settings"""
		cfg={ }
				
		for category in self.format :
			for name in self.format[category] :
				data_format=self.format[category][name]
				try:
					data=self.parser.get(category,name)
				except configparser.NoSectionError :
					### try to have the same argparse error behavior
					sys.exit(CFG_ERROR_MSG1.format(category))# write error on stderr					
				except configparser.NoOptionError :
					### try to have the same argparse error behavior
					sys.exit(CFG_ERROR_MSG2.format(name,category))# write error on stderr	
				else:
					#print( "[{}]{} {}".format(category,name,data) )
					data_list=shlex.split(data)
					data_qantum=len(data_list)
					#print(data_qantum,data_list)
					if ( data_qantum!=data_format["qantum"] and data_format["qantum"]!=0 ) or data_qantum==0 :
						### try to have the same argparse error behavior
						sys.exit(CFG_ERROR_MSG3.format(name,category))# write error on stderr	

					### config parser also provide getboolean() getint() and getfloat()
					### but it's not convenient to check format type and then using the matching parser method.
					for index in range(data_qantum) :
						data= data_list[index]
						
						if data_format["tip"]==bool :
							try:
								data= bool(util.strtobool(data))
							except:
								### try to have the same argparse error behavior
								sys.exit(CFG_ERROR_MSG3.format(name,category))# write error on stderr	
						else :
							try:
								data= data_format["tip"](data)
							except:
								### try to have the same argparse error behavior
								sys.exit(CFG_ERROR_MSG3.format(name,category))# write error on stderr	
								
						if data_format["choices"] and not data in data_format["choices"] :
							### try to have the same argparse error behavior
							sys.exit(CFG_ERROR_MSG3.format(name,category))# write error on stderr	

						data_list[index]=data
						
					else: # Executed if no break in for 
						if not category in cfg :
							cfg[category]={}
						if data_qantum==1 :
							cfg[category][name]=data_list[0]
						else :
							cfg[category][name]=data_list
				
		return cfg



class Command_line :
	"""comand line parser"""
	def __init__(self):
		#print(sys.argv)# print the full command line
		self.parser =  argparse.ArgumentParser(description=DESCRIPTION)#,allow_abbrev=False)
		#self.parser.add_argument('-v','--version',action='version',version=name+version,help=CMD_VERSION_MSG)

	def add_arg(self,arg,tip,qantum,help):
		"""specifies the request for one or more values ​​in the command line"""
		if qantum==0 : qantum='+' #convert to argparse nargs
		self.parser.add_argument(arg,type=tip,nargs=qantum,help=help)
		
	def add_choice(self,shortflag,longflag,tip,qantum,choices,help,category,name):
		"""for these flags in the command line chosen values will be stored"""
		index=category+CMD_INDEX_SEPARATOR+name
		if qantum==0 : qantum='+' #convert to argparse nargs
		self.parser.add_argument(shortflag,longflag,type=tip,nargs=qantum,choices=choices,help=help,dest=index)

	def add_positive_flag(self,shortflag,longflag,help,category,name):
		"""for these flags in the command line a True value will be stored"""
		index=category+CMD_INDEX_SEPARATOR+name
		self.parser.add_argument(shortflag,longflag,action='store_const',const=True,help=help,dest=index)

	def add_negative_flag(self,shortflag,longflag,help,category,name):
		"""for these flags in the command line a False value will be stored"""
		index=category+CMD_INDEX_SEPARATOR+name
		self.parser.add_argument(shortflag,longflag,action='store_const',const=False,help=help,dest=index)

	def add_valu(self,shortflag,longflag,tip,qantum,help,symbols,category,name):# tip can be : bool float int string any*
		"""for these flags in the command line one or many optional values will be stored"""
		index=category+CMD_INDEX_SEPARATOR+name
		if qantum==0 : qantum='+' #convert to argparse nargs
		self.parser.add_argument(shortflag,longflag,type=tip,nargs=qantum,help=help,metavar=symbols,dest=index)

	def get(self):
		"""return result of the parsed command line settings"""
		cmd={ }
		args = vars( self.parser.parse_args() )# vars return object attributes as dict.
		#print(args)
		for index in args.keys() :
			data=args[index]
			if data is not None :
				#print(index,data,type(data))#
				index=index.split(CMD_INDEX_SEPARATOR)
				if len(index)>1 :
					cat=index[0]
					name=index[1]
				else :
					cat=CMD_CAT_ARG
					name=index[0]
				if not cat in cmd :
					cmd[cat]={}
				if type(data)==list and len(data)==1 :
					data=data[0]
				cmd[cat][name]=data
		#print(cmd)
		return cmd

