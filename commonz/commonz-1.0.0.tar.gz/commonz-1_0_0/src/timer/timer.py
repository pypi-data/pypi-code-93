#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "module for time date laps and clocks"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2016"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### time n dates modules
import time	#Time access and conversions.
#import date
#import datetime	#Basic date and time types.
#import calendar	#Functions for working with calendars, including some emulation of the Unix cal program.
#import dateutils #a super datetime modul, allowing to get particular laps ,exemple: “+ 1 month” and managing recurent events.
#import pytz #good implementation of time zone  management in Python



def get_UTC_epoch():
	""" return number of seconds utc from UNIX epoch"""
	return time.time()


class Cronos :
	"""Chronometer watch"""
	def __init__(self):
		"""initialization"""
		self.start_time=0
		self.stop_time=0
		
	def get(self):
		"""get time laps"""
		return self.stop_time-self.start_time
		
	def start(self):
		"""Start Chronometer"""
		self.stop_time=0
		self.start_time=time.clock()
		
	def stop(self):
		"""Stop Chronometer"""	
		self.stop_time=time.clock()
		
		
class FPS :
	"""frames per second measurement"""
	def __init__(self):
		"""initialization"""
		self.start=0
		self.fps=0
	
	def get(self):
		"""get the fps"""
		return self.fps
		
	def count(self):
		"""indicates image displayed"""
		instant=time.clock()
		laps=(instant-self.start)
		if laps :
			self.fps=int(round(1./laps))
		else : 
			self.fps=None
		self.start=instant

