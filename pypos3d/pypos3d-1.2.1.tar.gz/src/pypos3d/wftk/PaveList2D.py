# -*- coding: utf-8 -*-
# package: pypos3d.wftk
from pypos3d.wftk.WFBasic import TexCoord2f

class PaveList2D(object): # Could be a list of TexCoord2f
  ''' PaveList2D is a two dimensional map of list for (x,y) tuple or TexCoord2f.
  PaveList2D provides a fast access and merge (n.log(n)).
  '''
 
  def __init__(self, n:int=16, texList=None):
    '''
    Create a PaveList2D of n x n case
     Optionaly filled with a list of TexCoord2f or a list of (x,y) floats
     Coordinates (x,y) shall be in [0.0, 1.0]
     The input texList is kept as is and may be modfied by insertions methods
   
    Parameters
    ----------
    n : int
      size of the map (default 16)

    texList : initial list of TexCoord2f
    '''
    self.init(n, texList)

  # 
  # Initialize the map
  #
  # @param n size of the map
  # @param texList list of input data
  #    
  def init(self, n, texList):
    self.__n = n
    self.__step = 1.0/float(n)
    self.__ground = [ None ]*(n*n)
    self.fill(texList)

  #
  # TODO: Implement (x,y) tuple
  #
  def fill(self, data):
    ''' Reset the map and fill it with the given data. '''
    self.__ground = [ None ]*(self.__n*self.__n)

    if not data:
      # Reset All
      self.__texList = []
      return

    maxn = self.__n-1
    if isinstance(data[0], TexCoord2f):
      self.__texList = data

      for i,t in enumerate(data):
        ix = min(int(t.x / self.__step), maxn) 
        iy = min(int(t.y / self.__step), maxn)
        paveno = self.__n*iy + ix
 
        if self.__ground[paveno]==None:
          self.__ground[paveno]=[]

        self.__ground[paveno].append(i)

    else: # The shall contain [x,y] or (x,y) data
      pass
    
  def statStr(self):
    ''' Return a statistic string about the PaveList2D. '''
    nbpave=0
    maxpt=0
    for pave in self.__ground:
      if pave:
        nbpave+=1
        maxpt = max(maxpt, len(pave))
        
    return 'PaveList2D[Size={0:d} Tx={1:d} Paves: {2:d}({3:.2f}%) maxLeafSize={4:d}]'.format(self.__n, len(self.__texList), \
          nbpave, 100.0*float(nbpave)/float(self.__n*self.__n), maxpt)
    
  def length(self):
    ''' Return the length of the texList. '''
    return len(self.__texList)

  #
  # TODO: Implement (x,y) tuple
  #
  def IndexAdd(self, tOrx, y=0.0):
    ''' Add the input TexCoord2f of tuple to the texList and return its index.
    '''
    if isinstance(tOrx, TexCoord2f):
      maxn = self.__n-1
      ix = min(int(tOrx.x / self.__step), maxn) 
      iy = min(int(tOrx.y / self.__step), maxn)
      paveno = self.__n*iy + ix
      
      if self.__ground[paveno]==None:
        self.__ground[paveno]=[]

      for idx in self.__ground[paveno]:
        if self.__texList[idx] == tOrx:
          break 
      else :
        idx = len(self.__texList)
        self.__texList.append(tOrx)
        self.__ground[paveno].append(idx)

    else:
      pass

    return idx

  #
  # TODO: Implement (x,y) tuple
  #
  def search(self, tOrx, y=0.0):
    ''' Return the index of a give TexCoord2f or (x,y) tuple -1 if not found. '''
    if isinstance(tOrx, TexCoord2f):
      maxn = self.__n-1
      ix = min(int(tOrx.x / self.__step), maxn) 
      iy = min(int(tOrx.y / self.__step), maxn)
      paveno = self.__n*iy + ix

      if self.__ground[paveno]:
        for idx in self.__ground[paveno]:
          if self.__texList[idx] == tOrx:
            return idx 
    else:
      pass

    return -1
  
  
  
  #
  #
  def addList(self, l):
    ''' Add a list of TexCoord2f or (x,y) tuples.
    Return a mapping table between input index and new indexes
    '''
    mapIdx = [-1]*len(l)
    for i,t in enumerate(l):
      mapIdx[i] = self.IndexAdd(t)
  
    return mapIdx
  
  #End of Class PaveList2D
