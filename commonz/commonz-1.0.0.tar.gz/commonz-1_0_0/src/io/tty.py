#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "module for input output on TeleTYpewriter(CLI)"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.1.1"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020-09-25"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
import threading # for Measure objects
import readline # makes easier to read/write history files and completion
import sys # use for output messages and pipe input
import os # for the newlines character
#import fileinput # open() alternativ, useful for opening multiple files at once or using a pipe shell |
#import pipes



def get_keyboard_input(prompt, prefill=''):
	"""prompts the user for usable input"""
	readline.set_startup_hook(lambda: readline.insert_text(prefill))
	try:
		return input(prompt)
	finally:
		readline.set_startup_hook()


def read_pipe_input():
	"""return pipe inputs"""
	#line=fileinput.input('-'))# blok if nothing is provided by the pipe
	line=sys.stdin.readline()#blok if nothing is provided by the pipe
	return line.rstrip(os.linesep)# remove ending newlines characters.
	
	
def print_info(message):
	"""print infonmessage on stderr output"""
	#sys.stdout.write(message)
	print(message,file=sys.stdout)
	
def print_error(message):
	"""print error message on stderr output"""
	#sys.stderr.write(message)
	print(message,file=sys.stderr)
	
	
class Measure(object):
	"""Calculation and display measurement of tasks progress"""

	def __init__(self,task_name,total):
		"""task_name will be display first on the command line 
		then total will be use for showing the completion"""
		self.task_name =task_name
		self.total = total
		self.amount = 0
		self.rate = 0
		self._lock = threading.Lock()

	def __call__(self,amount):
		"""add a completed amount of the task"""
		# To simplify we'll assume this is hooked up to a single filename.
		with self._lock:
			self.amount += amount
			self.rate = (self.amount/self.total)

	def display(self):
		"""Show the task progress measurement"""
		msg="\r{}:{:>4.0%}".format(self.task_name,self.rate)
		#sys.stdout.write(msg)
		#sys.stdout.flush()
		print(msg,file=sys.stderr,end='',flush=True)#if flush is true, the flow is forced to display.

	def end(self):
		"""end by showing a 100% task progress completion"""
		#sys.stdout.write("\n")
		#sys.stdout.flush()
		print(file=sys.stderr,flush=True)

