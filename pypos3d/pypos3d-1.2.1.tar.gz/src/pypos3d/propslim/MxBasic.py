'''
Created on 21 nov. 2020

@author: olivier
'''
import sys
import numpy as np
from numpy.linalg import LinAlgError
from pypos3d.wftk.WFBasic import Point3d


class MxHeapable: 
  def __init__(self): # MxHeapable()
    self.heapKey = 0.0 
    self.heapPos = -47
 
  def is_in_heap(self): return self.heapPos != -47 
  def not_in_heap(self): self.heapPos = -47
  def get_heap_pos(self): return self.heapPos
  def set_heap_pos(self, t): 
    self.heapPos = t
 
  # Very bad detailed design, even in C++
  def heap_key(self, k=sys.float_info.max):
    if k==sys.float_info.max:
      return self.heapKey
    else:
      self.heapKey = k  


class MxHeap:
  ''' Max Heap implementation for QSlim usage.
    Heapable objects must have two fields:
    - heapPos as integer, default "-47"
    - heapKey : a comparable value, default
    They can also inherit from MxHeapable.
    Anyway, for performance reason, named fields will be addressed directly. 
  '''
  
  def __init__(self, n=0):
    '''
    public MxHeap()
    public MxHeap(int n)
    '''
    if not n: n=8
    self.__fill = 0
    self.__block = [ None ] * n
 
  def get(self, i): return self.__block[i]

  def drop(self):
    self.__fill -= 1
    return self.__block[self.__fill]

  def __str__(self):
    return 'H({:d}/{:d} : {:s})'.format( self.__fill, len(self.__block), '['+ str( [ str(e)+', ' for e in self.__block[:self.__fill] ])+']')

  def __swap(self, i, j):
    self.__block[i], self.__block[j] = self.__block[j], self.__block[i]
    self.__block[i].set_heap_pos(i)
    self.__block[j].set_heap_pos(j)

  def __upheap(self, i):
    moving = self.__block[i] # get(i)
    index = i
    p = (i - 1) // 2 # self.__parent(i)

    while index > 0 and moving.heapKey > self.__block[p].heapKey:
      # self.__place(self.__block[p], index)
      x = self.__block[p]; self.__block[index] = x; x.heapPos = index      
      index = p
      p = (p - 1) // 2 # self.__parent(p)

    if index!= i:
      # self.__place(moving, index)
      self.__block[index] = moving; moving.heapPos = index      

  def length(self): return self.__fill

  def __downheap(self, i):
    moving = self.__block[i] # get(i)
    index = i
    l = 2 * i + 1 # self.__left(i)
    r = 2 * i + 2 # __right(i)

    while l < self.__fill:
      largest = r if (r < self.__fill and self.__block[l].heapKey < self.__block[r].heapKey) else l

      if moving.heap_key() < self.__block[largest].heapKey:
        #self.__place(self.__block[largest], index)
        x = self.__block[largest]; self.__block[index] = x; x.heapPos=index      

        index = largest
        l = 2 * index + 1 # self.__left(index)
        r = 2 * index + 2 # self.__right(index)
      else:
        break

    if index!=i:
      #self.__place(moving, index)
      self.__block[index] = moving; moving.heapPos=index      

  def insert(self, t, v=sys.float_info.max):
    '''
      def insert(self, t):
      self.insert(t, t.heap_key())
    '''
    if v==sys.float_info.max:
      v = t.heapKey
    else:
      t.heapKey = v
      
    # self.add(t) : Inlined
    if self.__fill == len(self.__block):
      self._resizeblock(len(self.__block) * 2)
    self.__block[self.__fill] = t
    i = self.__fill
    t.heapPos = i
    self.__fill+=1
    self.__upheap(i)

  #def last_id(self): return self.__fill - 1
  #def total_space(self): return len(self.__block)
  #def last(self): return self.__block[self.__fill-1]

  def _resizeblock(self, n):
    N = len(self.__block)
    if n==N: return

    if n<N:
      self.__block[:] = self.__block[0:n]
    else:
      self.__block += [ None ]*(n-N)


  def update(self, t, v=sys.float_info.max):
    ''' public void update(MxHeapable t, float v) '''
    if v==sys.float_info.max:
      v = t.heapKey
    else:
      t.heap_key(v)
     
    i = t.heapPos
    if i > 0 and v > self.__block[((i - 1) // 2)].heapKey:
      self.__upheap(i)
    else:
      self.__downheap(i)

  def extract(self):
    if self.__fill < 1:
      return None

    self.__swap(0, self.__fill - 1)
    dead = self.drop()
    self.__downheap(0)
    dead.heapPos = -47
    return dead

  def remove(self, t):
    if t.heapPos == -47:
      return None

    i = t.heapPos
    self.__swap(i, self.__fill - 1)
    self.drop()
    t.heapPos = -47

    if self.__block[i].heapKey < t.heapKey:
      self.__downheap(i)
    else:
      self.__upheap(i)

    return t

  


class MxQuadric:
  ''' public class MxQuadric implements Blockable '''
  def __init__(self, n=0, src:'MxQuadric' = None, p1=None, p2=None, p3=None, area=1.0, Q3:'MxQuadric3'=None):
    ''' Constructors: 
          public MxQuadric(int n)
          public MxQuadric(MxQuadric src)
          public MxQuadric(MxVector p1, MxVector p2, MxVector p3, double area /* =1.0 */)
          public MxQuadric(MxQuadric3 Q3, int n)
    '''
    self.valid = True
    
    if n:
      self.A = np.zeros((n,n))
      self.b = np.zeros((n,))
      self.clear(0.0)
      self.c = 0.0 # double c
      self.r = 0.0 # double
      
      if Q3:
        A3 = Q3.tensor()
        b3 = Q3.vector()

        for i in range(0,3):
          for j in range(0,3):
            self.A[i][j] = A3[i][j]
          self.b[i] = b3[i]

        self.c = Q3.offset()
        self.r = Q3.area()

    elif src:
      self.A = np.array(src.A)
      self.b = np.array(src.b)
      self.c = src.c
      self.r = src.r
    elif isinstance(p1, np.ndarray) and isinstance(p2, np.ndarray) and isinstance(p3, np.ndarray):
      self.build(p1, p2, p3, area)

  def build(self, p1, p2, p3, area=1.0):
      n = len(p1)
      A = np.eye(n)
      #self.b = np.zeros((n,))

      e1 = p2 - p1
      e1 /= np.linalg.norm(e1) # (); // e1 = p2-p1; unitize

      e2 = p3 - p1
      e2 -= e1 * e1.dot(e2)
      ne2 = np.linalg.norm(e2)
      if ne2==0.0:
        self.valid=False
      else:
        e2 /= ne2 # unitize(); // e2 = p3-p1-e1*(e1*(p3-p1)); unitize

      p1e1 = p1.dot(e1)
      p1e2 = p1.dot(e2)

      #MxQuadric.symmetric_subfrom(self.A, e1, e1)
      #MxQuadric.symmetric_subfrom(self.A, e2, e2)
      for i in range(0, n):
        for j in range(0, n):
          A[i][j] -= (e1[i]*e1[j] + e2[i]*e2[j]) 


      self.A = A
      # b = e1*p1e1 + e2*p1e2 - p1
      self.b = e1*p1e1 + e2*p1e2 - p1
      self.c = p1.dot(p1) - p1e1 * p1e1 - p1e2 * p1e2
      self.r = area

  def clear(self, val=0.0):
    self.A[:] = val
    self.b[:] = val
    self.c = val
    self.r = val


  def add(self, q:'MxQuadric'):
    self.A += q.A
    self.b += q.b
    self.c += q.c
    self.r += q.r
    return self

  def optimize(self, v:'MxVector'):
    try:
      Ainv = np.linalg.inv(self.A)
      v[:] = - Ainv.dot(self.b)
    except LinAlgError:
      return False

    return True

  def evaluate(self, v:'MxVector'):
    ''' evalute = operator(MxVector) '''
    tmpV = self.A.dot(v)
    return v.dot(tmpV) + 2.0 * self.b.dot(v) + self.c




class MxQuadric3:
  ''' 3D Quadric '''

  def init(self, a, b, c, d, area):
    self.a2 = a * a
    self.ab = a * b
    self.ac = a * c
    self.ad = a * d
    self.b2 = b * b
    self.bc = b * c
    self.bd = b * d
    self.c2 = c * c
    self.cd = c * d
    self.d2 = d * d
    self.r = area

  def __init__(self, n, d, area=1.0):
    ''' Constructor
      public MxQuadric3(float[] n, double d, double area /* =1.0 */)
      public MxQuadric3(Vec3 n, double d, double area /* =1.0 */) '''
    # self.init(n[0], n[1], n[2], d, area)
    self.init(n.x, n.y, n.z, d, area)

  def mul(self, s):
    #/ Scale coefficients
    self.a2 *= s
    self.ab *= s
    self.ac *= s
    self.ad *= s
    self.b2 *= s
    self.bc *= s
    self.bd *= s
    self.c2 *= s
    self.cd *= s
    self.d2 *= s

    return self

  def tensor(self):
    # return Mat3(new Vec3(a2, ab, ac), new Vec3(ab, b2, bc), new Vec3(ac, bc, c2))
    return np.array([[self.a2, self.ab, self.ac], [self.ab, self.b2, self.bc], [self.ac, self.bc, self.c2]])

  def vector(self):
    return Point3d(self.ad, self.bd, self.cd)

  def offset(self):
    return self.d2

  def area(self):
    return self.r


class MxPairContraction:  #public MxPairContraction()
  def __init__(self):
    self.v1 = 0
    self.v2 = 0
    self.dv1 = Point3d()
    self.dv2 = Point3d()
    self.delta_pivot = 0
    # Lists of face indexes
    self.delta_faces = [] 
    self.dead_faces = []


