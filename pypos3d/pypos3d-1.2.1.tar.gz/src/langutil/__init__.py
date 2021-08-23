# -*- coding: utf-8 -*-
__version__ = '1.6'
__author__  = 'Olivier DUFAILLY'
__license__ = 'BSD'

import os
import os.path
import gzip
import logging

# Usual and common return codes
C_CANCEL  = 0x100
C_WARNING = 0x010
C_OK      = 0
C_FAIL    = -3
C_FILE_NOT_FOUND = -4
C_UNKNOWN        = -5
C_ERROR   = -1000 # Should be a very wrong case

def GetLowExt(fn):
  ''' Return the file extension in lower char '''
  lfn = fn.lower()
  p = lfn.rfind('.')
  return lfn[p+1:] if p>0 else ''

def cmp(a, b):
  return (a > b) - (a < b) 

#-----------------------------------------------------------------------#
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


#
# Binary Search in an ordered table (ascending order)
#
# def Arrays_binarySearch(t, key):
#   ''' Locate the leftmost value exactly equal to x '''
#   i = bisect_left(t, key)
#   if i != len(t) and t[i] == key:
#     return i
#   return -1

# def getDirectory(path): --> use os.path.dirname

def RemoveExt(filename):
  posext = -1 if (filename == None) else filename.rfind('.')
  return filename[0:posext] if posext>0 else filename


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K


class UsageError(Exception):
  ''' Exception used to manage 'usage' errors:
  - Syntax Errors
  - User Input Errors
  - Missing actors, groups, ...
  '''
  def __init__(self, msg, *args):
    super().__init__(msg)
    


class LogStatus:
  ''' Simple Logging class used to return statuses of complex algorithms '''
  def __init__(self, usedLogging = True):
    self.ret = C_OK
    self.msg = ''
    self.uselog = usedLogging
    
  def info(self, msg='', *args):
    '''
    To be Overloaded for MMI purpose.
    Called by status(), worstStatus and logCond() methods
    '''
    sm = self.__class__.__name__  + ':' + msg.format(*args)
    self.msg = self.msg+' '+sm if self.msg else sm
    if self.uselog:
      logging.info(self.msg)
    return self.msg

  def status(self, ret=C_OK, msg='', *args):
    self.ret = ret
    if msg:
      self.info(msg, *args)
    return self.ret

  def worstStatus(self, ret=C_OK, msg='', *args):
    self.ret = min(ret, self.ret)
    if msg:
      self.info(msg, *args)
    return self.ret

  def logCond(self, cond, msg, *args):
    if cond:
      self.info(msg, *args)
    return cond
  
  def raiseCode(self, ret=C_OK, msg='', *args):
    if ret!=C_OK:
      self.status(ret=ret, msg=msg, *args)
      raise UsageError(msg, self)
    
  
