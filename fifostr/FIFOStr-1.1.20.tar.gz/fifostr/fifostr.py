#!/usr/bin/env python
"""
	fifostr.py - A FIFO (first in first out) buffer for strings derived from deque with pattern match trigger and callback capability
	
	@copy Copyright (C) <2011>  <M. A. Chatterjee>
	
	@author M A Chatterjee, deftio [at] deftio [dot] com
	
	-- full license below -- 
	Copyright (c) 2011-2016, M. A. Chatterjee <deftio at deftio dot com>
	All rights reserved.

	Redistribution and use in source and binary forms, with or without
	modification, are permitted provided that the following conditions are met:

	* Redistributions of source code must retain the above copyright notice, this
	  list of conditions and the following disclaimer.

	* Redistributions in binary form must reproduce the above copyright notice,
	  this list of conditions and the following disclaimer in the documentation
	  and/or other materials provided with the distribution.

	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
	AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
	IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
	DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
	FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
	DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
	SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
	CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
	OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
	OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

	-- end license --
	#this class should work on either python 2.7+ or python 3+ distributions
	#for performance notes see README.md
"""
#dependancies
#from collections import deque, Iterable

try:
    from collections.abc import deque, Iterable  # noqa
except ImportError:
    from collections import deque, Iterable  # noqa

import re 
import itertools
import sys
#import builtins

__author__ = 'M. A. Chatterjee'
__copyright__ = 'copyright (C) 2011-2018 M. A. Chatterjee'
__version_full__ = [1,1,20]   #allows mixed types e.g. 1,0,"92b"
__version__ = '.'.join(str(x) for x in __version_full__)

#FIFO (First-In-First-Out) String --> is a rolling FIFO of last n chars seen
#use addPattern() / delPattern() to add/delete patterns to look for in the fifo
#patterns can be strings, regular expressions (regex), or a user-supplied-function provided that
#the function takes a string, returns a bool

class FIFOStr(deque):
	def __init__(self, initparam=None):
		"""
		FIFOStr is a deque derived string class which has pattern matching abilities when new chars
		are added to its internal storage.

		FIFOStr may be unbounded in length as in 
		myFifoStr = FIFOStr()

		or may be set to a fixed length as in
		myFifoStr = FIFOStr(10)   #sets a fifostr object with a fixed length of 10 chars

		or it can be initialized from a string 
		myfifostr = FIFOStr("this is my string")

		patterns can be strings, regular expressions, or user supplied parsers.  when a character is added to 
		fifostr each stored pattern is checked to see if a match is found.  If a match is found then a user supplied
		callback function is invoked.  Any number of patterns (which can be overlapping) can trigger the supplied
		callback functions.

		Args:
		    size (int, optional): set size of the fifostr object.  unbounded if omitted.
		    or
		    string (optional) : set size of fifostr object from length of a string and assign initial value to from that string

		"""
		initsize = initparam
		
		if type(initparam) ==  str:  #treat argument as a string, set length to the string's length
			initsize = len(initparam)

		super( FIFOStr, self ).__init__(maxlen=initsize) #inheritance from deque
		self.patterns 	= {} #dict of patterns to search for
		self.patternIdx = 0
		
		if (type(initparam) == str):  #since the initial param was a str we now set the deque to that string
			deque.__iadd__(self,initparam)

		def enum(**enums):
			"""
			Simple constant ENUM style generator used for indexing internal storage array
			"""
			return type('Enum', (), enums)

		self.PIDX = enum(PATTERN=0, START=1, END=2, CALLBACKFN=3, LABEL=4, ACTIVE=5) #used internally

	@staticmethod
	def fifodisplay(x):
	    d = sys.__fifostr_prev_displayhook__
	    #builtins._ = None
	    if type(x) == type(FIFOStr(1)):
	        d(str(x))
	    else:
	        d(x)

		



	def typeStr(self,x):
		"""
		returns the type of an entity as a str.  used internally for pattern match storage and logic

		Args:
			x: entity to find the type of

		Returns:
			str: entity type as a string
		"""
		xt = str(type(x))
		def f(): return
		t = {
			str(type(123))	:"int",
			str(type(0.1)) : "float",
			str(type(re.compile(""))): "regex",
			str(type(self.head)):"function", #note raw type is 'instancemethod'
			str(type(f)):"function",
			str(type("")):"str",
			str(type(FIFOStr)):"class"
		}
		tr = xt
		if (xt) in t:
			tr = t[xt]
		return tr

	def iterable(self,obj):
		"""
		checker for iterability for some ops.  actually I was just very iterable when I realised this 
		wasn't a built in in the language  ;)

		Args:
			obj : object to make iterable

		Returns:
			bool: whether object is iterable
		"""
		return isinstance(obj, Iterable)

    #head,tail,all operations ==============================================
	def head(self,l=1):
		"""
		fetch beginning n chars of fifostr

		Args:
			l (int, optional) : number of chars of beginning of string to get. defaults to 1
		Returns:
			str
		"""
		if len(self)<l: 
		    l=len(self)
		return "".join([self[i] for i in range(l)])
    
	def tail(self,l=1):
		"""
		get last n chars of fifostr

		Args:
			l (int, optional) : number of chars of beginning of string to get. defaults to 1

		Returns:
			str
		"""
		if len(self)<l: 
		    l=len(self)
		return "".join([self[i] for i in range(len(self)-l,len(self))])
    
	def all(self):
		"""
		get all chars of fifostr as a str

		Args:
			none

		Returns:
			str
		"""
		return "".join(self)

	#simple tests for equality at head/tail/all given a string ===============
	def eqhead(self,instring):
		"""
		test if a string matches the beginning chars of the fifostr

		Args:
			instring (str) : str to compare head to

		Returns:
			bool: True if exact match else False
		"""		
		return self.head(len(instring))==instring    
    
	def eqtail(self,instring):
		"""
		test if a string matches the end chars of the fifostr

		Args:
			instring (str) : str to compare tail to

		Returns:
			bool: True if exact match else False
		"""				
		return self.tail(len(instring))==instring

	def eq(self,instring):
		"""
		test if a string matches entire fifostr

		Args:
			instring (str) : str to compare entire fifostr to

		Returns:
			bool: True if exact match else False
		"""				
		return self.all()==instring

	#overides================================================================
	def append(self,x,inc=False): 
		"""
		add char(s) to the right end of the fifostr 
		does not increase the size of the fifostr if maxlen is set

		Args:
			x (str) : str to add
			inc (bool) : whether to ingest all of x at once (default) or if True add each char in x one at a time.
				this allows each permutation of fifostr to be tested against all active stored patterns

		Returns:
			fifostr object (mutable)
		"""		
		x = str(x)
		if inc==False: #this will append all of x at once
			deque.append(self,x)
			if len(self.patterns)>0:
				self.testAllPatterns(doCallbacks=True,retnList=False)
		else: #do each append, one at a time, so that all patterns can be checked
			for i in range(len(x)):
				deque.append(self,x[i])
				#todo do inc handling
				if len(self.patterns)>0:
					self.testAllPatterns(doCallbacks=True,retnList=False)
		return self

	def appendleft(self,x,inc=False): 
		"""
		add char(s) to the left end of the fifostr
		does not increase the size of the fifostr if maxlen is set

		Args:
			x (str) : str to add
			inc (bool) : whether to ingest all of x at once (default) or if True add each char in x one at a time.
				this allows each permutation of fifostr to be tested against all active stored patterns

		Returns:
			fifostr object (mutable)
		"""
		x = str(x)
		if inc==False: #this will appendleft all of x at once
			deque.appendleft(self,x)		
			if len(self.patterns)>0:
				self.testAllPatterns(doCallbacks=True,retnList=False)
		else: #do each appendleft, one at a time, so that all patterns can be checked
			for i in range(len(x)):
				deque.appendleft(self,x[i])		
				if len(self.patterns)>0:
					self.testAllPatterns(doCallbacks=True,retnList=False)		
		return self

	def extend(self,x): 
		"""
		add char(s) to the right end of the fifostr 
		does not increase the size of the fifostr if maxlen is set

		Args:
			x (iterable) : str to add

		Returns:
			fifostr object (mutable)
		"""		
		for i in range(len(x)):
			deque.extend(self,str(x[i]))
			#todo do inc handling
			if len(self.patterns)>0:
				self.testAllPatterns(doCallbacks=True,retnList=False)
		return self

	def extendleft (self,x): 
		"""
		add char(s) to the left end of the fifostr
		does not increase the size of the fifostr if maxlen is set

		Args:
			x (iterable) : str to add

		Returns:
			fifostr object (mutable)
		"""
		for i in range(len(x)):
			deque.extendleft(self,str(x[i]))	
			if len(self.patterns)>0:
				self.testAllPatterns(doCallbacks=True,retnList=False)		
		return self

	def rotate(self,x,inc=False): 
		"""
		rotate the chars in fifostr by x positions.  chars moved off the right end are put back on the left.

		Args:
			x (int) : number of positions to rotate
			inc (bool) : whether to rorate all of x at once (default) or if True rorate each char one at a time.
				this allows each permutation of fifostr to be tested against all active stored patterns

		Returns:
			fifostr object (mutable)
		"""
		if inc==False: #this will rotate all of x at once
			deque.rotate(self,x)
			if len(self.patterns)>0:
				self.testAllPatterns(doCallbacks=True,retnList=False)
		else:
			for i in range(x):
				deque.rotate(self,1) #1 at a time..
				if len(self.patterns)>0:
					self.testAllPatterns(doCallbacks=True,retnList=False)
		return self

	def pop(self): 
		"""
		return the right most char from fifostr and shorten fifostr by 1 entry
		after pop() all active stored patterns are checked for matches

		Args:
			None

		Returns:
			fifostr object (mutable)
		"""
		x=deque.pop(self)
		if len(self.patterns)>0:
			self.testAllPatterns(doCallbacks=True,retnList=False)
		return x

	def popleft(self): 
		"""
		return the left most char from fifostr and shorten fifostr by 1 entry
		after pop() all active stored patterns are checked for matches

		Args:
			None

		Returns:
			fifostr object (mutable)
		"""		
		x=deque.popleft(self)
		if len(self.patterns)>0:
			self.testAllPatterns(doCallbacks=True,retnList=False)
		return x

	def remove(self,value): 
		"""
		remove all occurences of the a specific value from fifostr and shorten length by number of occurrences found

		Args:
			value (str) : value to remove (string of length 1 char)

		Returns:
			fifostr object (mutable)
		"""		
		deque.remove(self,value)
		if len(self.patterns)>0:
			self.testAllPatterns(doCallbacks=True,retnList=False)
		return self

	def reverse(self): 
		"""
		flip fifostr about its center
		after reversing all active stored patterns are checked for matches

		Args:
			None

		Returns:
			fifostr object (mutable)
		"""		
		deque.reverse(self)
		if len(self.patterns)>0:
			self.testAllPatterns(doCallbacks=True,retnList=False)
		return self

	#operators================================================================
	def __eq__(self,x):
		"""
		test if a string matches fifostr

		Args:
			x (str): string to match

		Returns:
			True if match, else False
		"""	
		return self.all()==x

	def __iadd__(self,x):
		"""
		add a string via the += operator

		Args:
			x (str or int or float): string to add

		Returns:
			fifostr object (mutable)
		"""			
		if isinstance(x,int) or isinstance(x,float):
			x=str(x)

		deque.__iadd__(self,x)
		if len(self.patterns)>0:
			self.testAllPatterns(doCallbacks=True,retnList=False)
		return self

	def __getitem__(self, index): 
		"""
		get a substring from fifostr operator.  supports int index, slices, and lists

		Args:
			index (str): string to match

		Returns:
			str
		"""	
		if isinstance(index, slice):
			s = index.start
			e = index.stop
			if (e=='$') or (e== None): # the character "$" is used to specify end-of-string anchor in regex, so also allowed here
				e=len(self)
			if (e < 0):
				e = len(self)+e  
			if (s=='^') or (s==None):  # the character "^" is used to specifiy start-of-string anchor in regex, so also allowed here
				s=0
			if (s<0):
				s= len(self)+s
			return "".join(itertools.islice(self, s, e, index.step))
		if isinstance(index, list):
			return "".join([deque.__getitem__(self, x) for x in index])
		if isinstance(index, tuple):
			return "".join([deque.__getitem__(self, x) for x in index])
		if isinstance(index, str):
			if index == '$':
				index = len(self) -1
			if index == "^":
				index = 0
		return str(deque.__getitem__(self, index))
	
	def __setitem__(self, key, value):
		"""
		set char in fifostr supplied position
		myFifostr[5] = 'm' #set fifostr position 5 to the character 'm'

		Args:
			key (int): index of char to set
			value (str): character value for fifostr[key] to be set to


		Returns:
			fifostr (mutable)
		"""	
		value = str(value)
		deque.__setitem__(self,key, value)
		if len(self.patterns)>0:
			self.testAllPatterns(doCallbacks=True,retnList=False)
		return self

	def __str__(self):
		return self.all()

	def __add__(self,other):
		return self.all()+str(other)

	def __radd__ (self,other):
		return str(other)+self.all()

	#pattern handling==========================================================
	def testPattern(self, pattern, start=0,end='$'):
		"""
		test if a pattern matches fifostr between supplied indeces

		Args:
			pattern (str or regex or function): pattern to match.  if str then it looks for an exact match. if
			regex then it looks to see if there is atleast one match.  if function it passes fifstr (as a str)
			to the function and expects function to equate to a boolean value.

			start (int or '^'): beginning position to look for matches.  default is 0.  the "^" means start of fifostr 
			end (int or '$'): end position to look for matches.  default is $.  the "$" means start of fifostr. $ is useful since if the fifostr maxlen is changed
			the $ param will still insure end-matching is still completed.

		Returns:
			True if match, else False
		"""		
		if start == '^':
			start = 0
		if end == '$':
			end = len(self)
		s=self[start:end]		
		pt = self.typeStr(pattern)
		#cheesy dynamic type handling here...  
		if (pt=="str"):  		#test match if pattern is == string 
			if pattern==s:
				return True
		elif (pt=="regex"): 	#if the regex matches using re.search() return True
			if pattern.search(s) != None:
				return True
		elif (pt=="function"):  #if its a function then we pass the string to the function
			return pattern(s)==True #enforces primitive casting to boolean
		#else pattern is not allowable type...
		return False

	def testAllPatterns(self,doCallbacks=False,retnList=True): 
		"""
		test all patterns stored in fifostr object for matches.

		Args:
			doCallbacks (bool, optional) : test each pattern and call the associated callback function if the pattern matches.
				default is False

			retnList (bool, optional) : return a list of which patterns matched.

		Returns:
			if retnList is True returns list of matches else returns number of matches as int.
		"""			
		l = []
		c = 0
		for i in self.patterns: #todo replace with map()
			if (self.patterns[i][self.PIDX.ACTIVE]): #is an active pattern 
				r=self.testPattern(self.patterns[i][self.PIDX.PATTERN],self.patterns[i][self.PIDX.START] ,self.patterns[i][self.PIDX.END])
				if (retnList):
					l.append([i,self.patterns[i][self.PIDX.LABEL],r])
				else:
					c=c+1
				if (doCallbacks):
					if r and (self.patterns[i][self.PIDX.CALLBACKFN] != None):
						self.patterns[i][self.PIDX.CALLBACKFN](self[self.patterns[i][self.PIDX.START]:self.patterns[i][self.PIDX.END]],self.patterns[i][self.PIDX.LABEL])
		if retnList:
			return l
		return c #if not returning list, then return the # of matched patterns

	def addPattern(self, pattern, callbackfn = None, start=0, end='$',label="",active=True): 
		"""
		add a pattern to the fifostr internal pattern storage.

		Args:
			pattern (str or regex or function): pattern to match.  if str then it looks for an exact match. if
			regex then it looks to see if there is atleast one match.  if function it passes fifstr (as a str)
			to the function and expects function to equate to a boolean value.

			callbackfn: a function to call when the supplied pattern is detected in fifostr object.  callback is passed the matching string (between start,end) and
				the label (if any)

			start (int or '^'): beginning position to look for matches.  default is 0.  the "^" means start of fifostr 
			
			end (int or '$'): end position to look for matches.  default is $.  the "$" means start of fifostr. $ is useful since if the fifostr maxlen is changed
			the $ param will still insure end-matching is still completed.

			label (str) : a label to call this match.  this label is passed to the callback_function when a match is found.

			active (boolean, optional) : whether this pattern is to tested each time fifostr is modified.  default is True.


		Returns:
			int : index of pattern stored.  this can be used to setActiveState or to delete the pattern later.
		"""				
		n = self.patternIdx
		self.patterns[n] = [pattern,start,end,callbackfn,label,active] #note order is important since used elsewhere
		#self.PIDX = enum(PATTERN=0, START=1, END=2, CALLBACKFN=3, LABEL=4, ACTIVE=5)  # see declaration above class def
		self.patternIdx += 1

		return n

	def delPattern(self,index): 
		"""
		delete a pattern from fifostr pattern storage

		Args:
			index (int) : id of pattern to be removed.

		Returns:
			number of stored patterns remaining
		"""
		if (index in self.patterns):
			del self.patterns[index] # don't do this --> this will mess up indexes to existing patterns the user may have
		return len(self.patterns)

	def getPattern(self,index): 
		"""
		get a stored pattern 

		Args:
			index (int): index for pattern to get.  index is the one returned from

		Returns:
			True if match, else False
		"""		
		if (index in self.patterns):
			return list(self.patterns[index])
		return None		

	def findPatternByLabel(self,label): #allows string or compiled regex
		"""
		find a pattern from fifostr pattern storage by its label

		Args:
			label (str) : label of pattern(s) to find

		Returns:
			list of matching patterns or None if not found
		"""
		r=[]
		if self.typeStr(label)=="str":
			for i in self.patterns:
				if self.patterns[i][self.PIDX.LABEL] == label:
					r.append(list(self.patterns[i]))
		elif self.typeStr(label)=="regex":
			for i in self.patterns:
				if label.search(self.patterns[i][self.PIDX.LABEL]) != None:
					r.append(list(self.patterns[i]))
		return r

	def setPatternActiveState(self,index,state): 
		"""
		set a pattern's active state.  If a pattern is active it will be test each time character(s) are added to fifostr else the pattern is skipped.

		Args:
			index (int) : id of pattern to set active state
			state (bool) : True for active, False for inactive

		Returns:
			current pattern state after setting
		"""
		if (index in self.patterns):
			self.patterns[index][self.PIDX.ACTIVE] = state==True
		return state==True

	def getPatternActiveState(self,index): 
		"""
		get a pattern's active state.  If a pattern is active it will be test each time character(s) are added to fifostr else the pattern is skipped.

		Args:
			index (int) : id of pattern to set active state

		Returns:
			bool: current pattern state
		"""
		if (index in self.patterns):
			return self.patterns[index][self.PIDX.ACTIVE]
		return -1 #error in index


	def showPatterns(self): #get all patterns stored
		"""
		get a list of all the current stored patterns

		Args:
			None

		Returns:
			list of any stored patterns
		"""
		return dict(self.patterns) #return shallow copy of current patterns

	def clearPatterns(self): 
		"""
		remove all patterns from fifostr pattern storage

		Args:
			None

		Returns:
			0
		"""
		self.patterns={}
		return self.numPatterns()

	def numPatterns(self):	 #show number of patterns in the search dictionary
		"""
		return number of active patterns

		Args:
			None

		Returns:
			int : number of stored patterns
		"""
		return len(self.patterns)

	#version info
	def ver(self):
		"""
		ver returns the version info of this library

		Returns:
			dict: containing current version
		"""
		v = {
				"version_str" :  __version__,
				"version" : __version_full__,
				"url" : "https://github.com/deftio/fifostr"					 
			}
			
		return 	v


if sys.displayhook != FIFOStr.fifodisplay:
	sys.__fifostr_prev_displayhook__ = sys.displayhook
	sys.displayhook = FIFOStr.fifodisplay
