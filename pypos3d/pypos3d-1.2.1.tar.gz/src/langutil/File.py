'''
Created on 10 mai 2020

@author: olivier
'''

import os.path

class File(object):
  '''
  Simple port of java.io.File
  '''

  def __init__(self, *args):
    '''
    Constructor
    '''
    self.__canonPath = args[0] if args[0] else ''
      
 
  
  def getName(self):
    lastSep = self.__canonPath.rfind(os.sep)
    return self.__canonPath[lastSep+1:] if lastSep>0 else self.__canonPath
  
  def getCanonicalPath(self):
    return self.__canonPath
  
  def exists(self):
    return os.path.exists(self.__canonPath)
    
  def isFile(self):
    return os.path.isfile(self.__canonPath)


  @classmethod
  def finder(clz, fname, imgdirpath='', throwFNF=True, fileExt=[], retFile=False, deepSearch=False, caseSensitive=True):
    ''' Search the given filename in the list of os.pathsep separated directories.
    Search first in current directory.
    When the file can not be found (or if it is an empty or null string):
      Throw (raise) FileNotFound exception if throwFNF is True,
      Else return None

    TODO: implement a recursive deep search and non case-sensitive search (Windows like)
    
    Parameters
    ----------
    fname : str
      Filename (or relative path) to search for.
      The extension may be omited if fileExt not empty
      
    imgdirpath : str, default empty
      List of directory path separated by os.sep (i.e ':' on Linux,  ';' on Windwows)
      
    throwFNF : boolean, optional, default True
      When True finder raises a FileNotFound exception in case of no result
      Else finder returns None
      
    fileExt : list of str, optional, default is empty
      list of file extensions to be used for file search
      example: fileExt=('.zip', '.7z')
      
    retFile : boolean, optional, default is False
      When True finder returns an instance of 'File', else returns a string
      
    deepSearch : Not Implemented yet  
    caseSentivite : Not Implemented yet  
      
    Return:
      File or str : The first found file, else None if not found and throwFNF is false
    
    '''
    if fname:
      tabpath = ['', '.', ] + imgdirpath.split(os.pathsep)
      tabPotFileName = [ fname, ]
      if fileExt:
        p = fname.rfind('.')
        fBaseName = fname[:p] if p>0 else fname
        tabPotFileName += [ fBaseName + ext for ext in fileExt ]        
        
      for path in tabpath:
        for fn in tabPotFileName:
          testfn = os.path.join(path, fn)
          if os.path.isfile(testfn):
            return File(testfn) if retFile else testfn

    if throwFNF:
      raise FileNotFoundError()
    else:
      return None

  @classmethod
  def writable(clz, fname, dirpathlist='', throwFNF=True, caseSensitive=True):
    ''' Search if the given filename can be created in the list of os.pathsep separated directories.
    Search first in current directory.
    When the file can not be found (or if it is an empty or null string):
      Throw (raise) FileNotFound exception if throwFNF is True,
      Else return None
    '''
    if fname:
      # Separate the directory from the filename itself
      dn = os.path.dirname(fname)
      
      tabpath = ['.', ] + dirpathlist.split(os.pathsep)
      for path in tabpath:
        testfn = os.path.join(path, dn)
        if os.path.isdir(testfn):
          # The directory exists
          return os.path.join(path, fname)

    if throwFNF:
      raise FileNotFoundError('Missing Directory for:'+fname if fname else '')
    else:
      return None




