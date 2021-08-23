# -*- coding: UTF-8 -*-
# package: pypos3d.wftk

import sys, os, gzip, math, copy
import collections
from typing import NamedTuple
import numpy as np
from scipy import interpolate


from langutil import C_OK, C_ERROR, C_FAIL, switch

PYPOS3D_TRACE=False

# 
# Constants used by the WaveFront geometrical package.
#  
C_COLINEAR_CROSS   = 0x0041
C_COLINEAR         = 0x0040
C_NOT_COPLANAR     = 0x0020
C_INTERSECT        = 0x0001

C_BAD_DELTAINDEX   = 0x0012
C_BAD_DELTACOUNT   = 0x0011
C_NODELTA          = 0x0010
C_VERTEX_NOT_FOUND = -5
C_MISSING_MAT      = -100
C_MISSING_FACEMAT  = -110

# TODO: for optim Add -FEPSILON
FEPSILON = 1e-6
FEPSILON2 = FEPSILON*FEPSILON

# -------------------------------------------
# Face Attributs
# Face attributs are expressed with a 32bits motif
#  8 left bits are the binary attributes:
# 24 right bits are the material index
#
C_FACE_NONE     = 0x00000000
C_FACE_TEXT     = 0x01000000
C_FACE_NORM     = 0x02000000
C_FACE_TEXTNORM = C_FACE_TEXT|C_FACE_NORM
C_FACE_NOTEXT   = not C_FACE_TEXT
C_FACE_NONROM   = not C_FACE_NORM
C_FACE_MATMASK  = 0x00ffffff

#
def getOBJFile(filename):
  ''' Return the file descriptor of a OBJ or OBZ geometry.
  OBJ file is searched first.

  Parameters
  ----------
  filename : str
    Filename to open
  '''
  lfn = filename.lower()
  p = lfn.rfind('.obj')

  if os.path.isfile(filename):
    fic = open(filename, 'rt', errors='replace') if p>0 else gzip.open(filename, 'rt', errors='replace') 
  else:
    # Change for the other extension
    if p>0:
      fic = gzip.open(filename[0:p] + '.obz', 'rt', errors='replace') 
    else:
      p=lfn.rfind('.obz')
      fic = open(filename[0:p] + '.obj', 'rt', errors='replace') 

  return fic


def existGeom(filename):
  ''' Returns True if the WaveFront file exists.
  Look first for the file and then for the compressed version .obz

  Parameters
  ----------
  filename : str
    Filename to open
  '''
  if not os.path.isfile(filename):
    lfn = filename.lower()
    p=lfn.find('.obz')
    if p>0:
      # Searching: + filename[0:p] + '.obj' 
      return os.path.isfile(filename[0:p] + '.obj') 
    else:
      p=lfn.find('.obj')
      # Searching: + filename[0:p] + '.obz' 
      return os.path.isfile(filename[0:p] + '.obz') if p>0 else False

  return True

# Compute simple hashCode (sum of values)
# public final static int hashSomme(int[] src) --> Replaced by sum() in Python

def LowestIdxPos(idxTab):
  ''' Find the position of the lowest index. 
  
  Parameters
  ----------
  idxTab : list of int
        Table of indexes

  Returns
  -------
  int
    the index of the lowset value

  '''
  # Find lowest index
  lowestIdx = sys.maxsize
  pos = 0
  for i in range(0, len(idxTab)):
    if (lowestIdx > idxTab[i]):
      lowestIdx = idxTab[i]
      pos = i
  return pos

# def findCommonPoints(gBasSrcTbl, gHautSrcTbl):  --> Inlined
#   ''' Return the sorted list of common values between input lists '''
#   r = list(set(gBasSrcTbl) & set(gHautSrcTbl))
#   r.sort()
#   return r

# -------------------------------------------------------------------
def IndexAdd(l,p):
  ''' Return the index of the point in the list. 
  Add it if needed

  Parameters
  ----------
  l : list of Point
    Table of Points (or any comparable)

  p : a Point
    a Points (or any comparable) to find or to add

  Returns
  -------
  int
    the index of the Point
  '''
  try:
    return l.index(p)
  except ValueError:
    i = len(l)
    l.append(p)
    return i

def SArcCos(a,b):
  ''' Perform acos( a / b ) with rounding effects '''
  if math.fabs(b)>FEPSILON:
    r = a / b
    r = -1.0 if r<-1.0 else (1.0 if r>1.0 else r)
    return math.acos(r)
  else:
    return 0.0

def SArcSin(a,b):
  ''' Perform asin( a / b ) with rounding effects '''
  if math.fabs(b)>FEPSILON:
    r = a / b
    r = -1.0 if r<-1.0 else (1.0 if r>1.0 else r)
    return math.asin(r)
  else:
    return 1.0


# Used as base Object for Vector3d
class Point3d(object):
  ''' Simple 3D point class (mutable). '''
  
  #__hash__ = object.__hash__
  
  def __init__(self, x=0.0, y=0.0, z=0.0):
    ''' Create a new Point3d from various inputs.

    Point3d() --> (0.0, 0.0, 0.0)
    Point3d(X,Y,Z as float) --> (X, Y, Z)
    Point3d(P as Point3d) --> (p.x, p.y, p.z)
    Point3d([X,Y,Z]) --> ([0], [1], [2])

    Parameters
    ----------
    x : float (default 0.0) or Point3d or list or tuple
      X coordinate or global value if not float
    y : float (default 0.0)
      Y coordinate
    z : float (default 0.0)
      Z coordinate

    '''
    if isinstance(x, Point3d):
      self.x = x.x 
      self.y = x.y 
      self.z = x.z 
    elif isinstance(x, float):
      self.x = x 
      self.y = y 
      self.z = z 
    else: # x is supposed to be a table of 3 floats
      self.x = x[0]
      self.y = x[1] 
      self.z = x[2]
      

  def set(self, x=0.0, y=0.0, z=0.0):
    ''' Fill a Point3d with various inputs.
    Arguments similar to __init__
    '''
    if isinstance(x, Point3d):
      self.x = x.x 
      self.y = x.y 
      self.z = x.z 
    elif isinstance(x, float):
      self.x = x 
      self.y = y 
      self.z = z 
    else: # x is supposed to be a table of 3 floats
      self.x = x[0]
      self.y = x[1] 
      self.z = x[2]

    return self
      
  def X(self): return self.x
  
  def Y(self): return self.y
  
  def Z(self): return self.z

  def get(self,i): return self.x if i==0 else self.y if i==1 else self.z

  def __getitem__(self, i):
    if i==0:
      return self.x 
    elif i==1:
      return self.y 
    elif i==2:
      return self.z
    else:
      # Fix 20210626: Avoid Infinte loop in *()
      raise IndexError()

  def __eq__(self, other):
    ''' Compare two Point3d.

    Returns
    -------
    bool
      True if infinity-norm distance is smaller than FEPSILON
    '''
    return (math.fabs(other.x - self.x) < FEPSILON) and \
           (math.fabs(other.y - self.y) < FEPSILON) and \
           (math.fabs(other.z - self.z) < FEPSILON)

  def __le__(self, other):
    return NotImplemented
  
  def cross(self, v):
    ''' Compute the vector product self x v and return the result as a Point3d '''
    return Point3d(self.y * v.z - self.z * v.y, \
                   self.z * v.x - self.x * v.z, \
                   self.x * v.y - self.y * v.x)

  def isNull(self):
    ''' Check if a Point3d is null
    Returns
    -------
    bool
      True if the infinity-norm is smaller than FEPSILON
    '''
    return (math.fabs(self.x) < FEPSILON) and  \
           (math.fabs(self.y) < FEPSILON) and  \
           (math.fabs(self.z) < FEPSILON)
           
  # isNull for Square Vector < FEPSILON²
  def isNullProd(self):
    ''' Compare two Point3d (supposed to be result of a product (cross).
    Returns
    -------
    bool
      True if the infinity-norm is smaller than FEPSILON²
    '''
    return (math.fabs(self.x) < FEPSILON2) and  \
           (math.fabs(self.y) < FEPSILON2) and  \
           (math.fabs(self.z) < FEPSILON2)

  def dot(self, v):
    ''' Compute the scalar product self.v and return the result as a float '''
    return self.x * v.x + self.y * v.y + self.z * v.z

  def norme2(self):
    ''' Return the 2-norm² ''' 
    return self.x*self.x + self.y*self.y + self.z*self.z

  def norme(self):
    ''' Return the 2-norm ''' 
    return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

  def normalize(self):
    ''' Normalize a vector v/|v| if |v| not null, else does nothing '''
    n = self.norme()
    if n>0.0:
      self.x /= n
      self.y /= n
      self.z /= n

    return self

  def distance(self, other):
    ''' Return the 2-norm distance (euclidian) of the two points ''' 
    return math.sqrt( (other.x - self.x)*(other.x - self.x) +
                      (other.y - self.y)*(other.y - self.y) +
                      (other.z - self.z)*(other.z - self.z) )

  # public final static double dXY(Tuple3d t0, Tuple3d t1)
  def dXY(self, other):
    ''' Return the 2-norm distance of the two points on the Oxy plan ''' 
    return math.sqrt( (other.x - self.x)*(other.x - self.x) +
                      (other.y - self.y)*(other.y - self.y) )
            
  def distanceLinf(self, other):
    ''' Return the infinity-norm distance (euclidian) of the two points ''' 
    return max(abs(self.x-other.x), abs(self.y-other.y), abs(self.z-other.z))           

  def Lin33(self, M):
    ''' Return a new Point3d = M x self, where M is a 3x3 matrix '''
    mu = self.x*M[0][0] + self.y*M[0][1] + self.z*M[0][2] 
    mv = self.x*M[1][0] + self.y*M[1][1] + self.z*M[1][2] 
    mw = self.x*M[2][0] + self.y*M[2][1] + self.z*M[2][2] 
    return Point3d(mu, mv, mw)
  
  def inLin33(self, M):
    ''' Return and Modify self = M x self, where M is a 3x3 matrix '''
    mu = self.x*M[0][0] + self.y*M[0][1] + self.z*M[0][2] 
    mv = self.x*M[1][0] + self.y*M[1][1] + self.z*M[1][2] 
    mw = self.x*M[2][0] + self.y*M[2][1] + self.z*M[2][2] 
    self.x = mu
    self.y = mv
    self.z = mw
    return self
  
  
  @classmethod
  def parseVector3d(cls, val):
    ''' Parse a String containing 3 doubles and returns a 3D Vector.

    Parameters
    ----------
    val : str
      Input string of 3 floats - "example 0.1 -5.6 0.324654"

    Returns
    -------
    Vector3d
      The Vector3d representation of the string. None in case of error
    '''
    if val:
      vals = val.split()
      if len(vals) > 0:
        return Vector3d( float(vals[0]), float(vals[1]), float(vals[2]))

    return None


  def sub(self, v, v2=None):
    ''' Return if not v2 self - v else set self with v-v2 (to match javax.Vector3d behavior) '''
    if v2:
      if isinstance(v, Point3d):
        self.x = v.x - v2.x
        self.y = v.y - v2.y
        self.z = v.z - v2.z
      else:
        self.x = v[0] - v2.x
        self.y = v[1] - v2.y
        self.z = v[2] - v2.z
    else:
      if isinstance(v, Point3d):
        self.x -= v.x
        self.y -= v.y
        self.z -= v.z
      else:
        self.x -= v[0]
        self.y -= v[1]
        self.z -= v[2]

    return self


  # Return if not v2 self + v
  #   else set current with v+v2 (to match javax.Vector3d)
  def add(self, v, v2=None):
    ''' Return if not v2 self+v else set self with v+v2 (to match javax.Vector3d behavior) '''
    if v2:
      if isinstance(v, Point3d):
        self.x = v.x + v2.x
        self.y = v.y + v2.y
        self.z = v.z + v2.z
      else:
        self.x = v[0] + v2.x
        self.y = v[1] + v2.y
        self.z = v[2] + v2.z
    else:
      if isinstance(v, Point3d):
        self.x += v.x
        self.y += v.y
        self.z += v.z
      else:
        self.x += v[0]
        self.y += v[1]
        self.z += v[2]

    return self
  
  def scale(self, scalaire):
    ''' Multiply self by a scalar (float) '''
    self.x *= scalaire
    self.y *= scalaire
    self.z *= scalaire
    return self

  def scaleAdd(self, s, t1, t2):
    ''' Sets the value of this Point3d to the scalar multiplication of tuple t1 and then adds tuple t2. 
    self = s*t1 + t2.

    Parameters
    ----------
    s : float
      The scalar value
    
    t1 : Point3d
      The tuple to be multipled

    t2 : Point3d 
      The tuple to be added
  
    Return
    ------
    self
    '''
    self.x = t2.x + s*t1.x
    self.y = t2.y + s*t1.y
    self.z = t2.z + s*t1.z

    return self

  def __str__(self, *args, **kwargs):
    return 'P({0:.6g},{1:.6g},{2:.6g})'.format(self.x, self.y, self.z)
    
  def poserPrint(self):
    return '{0: 11.8f} {1: 11.8f} {2: 11.8f}'.format(self.x, self.y, self.z)
    
  def distanceSquared(self, t1):
    ''' Return Squared distance (euclidian) between t0 and t1
  #   * @param t0  First tuple (RO)
  #   * @param t1  First tuple (RO)
  #   * @return    the squared distance 
    '''
    if isinstance(t1, Point3d):
      return (self.x - t1.x) * (self.x - t1.x) + (self.y - t1.y) * (self.y - t1.y) + (self.z - t1.z) * (self.z - t1.z)
    else:
      return (self.x - t1[0]) * (self.x - t1[0]) + (self.y - t1[1]) * (self.y - t1[1]) + (self.z - t1[2]) * (self.z - t1[2])

  def neg(self):
    self.x = -self.x
    self.y = -self.y
    self.z = -self.z
    return self

  def __add__(self, other):
    return Point3d(self).add(other)

  def __sub__(self, other):
    return Point3d(self).sub(other)
  
  # Methods added for the decimate algorithm
  # public static Vec3 triangle_raw_normal(Vec3 v1, Vec3 v2, Vec3 v3)
  @classmethod
  def triangle_raw_normal(cls, v1, v2, v3):
    v21 = Point3d(v2).sub(v1)
    v31 = Point3d(v3).sub(v1)
    return v21.cross(v31)

  # public static Vec3 triangle_normal(Vec3 v1, Vec3 v2, Vec3 v3)
  @classmethod
  def triangle_normal(cls, v1, v2, v3):
    n = Point3d.triangle_raw_normal(v1, v2, v3)
    n.normalize()
    return n

  @classmethod
  def triangle_orientation(cls, p0, p1, p2, AxisOrder='xyz', inDegrees=False):
    ''' Compute the set of rotations (RotX, RotY, RotZ) that put the first axis of
    AxisOrder on the normal of the triangle.

    Parameters
    ----------
    p1, p2, p3 : Point3d
      Triangle definition

    AxisOrder : str, defaul 'xyz'
      Rotation order between 'xyz', 'yzx' and 'zxy'

    inDegrees : bool, default False
      if True returns the orientation in degrees
      else orientation is in radians

    Return
    ------
    Vector3d
      The result rotation vector
    '''
    
    n = Point3d.triangle_normal(p0, p1, p2)
    
    rotx, roty, rotz = 0.0,0.0,0.0
     
    if AxisOrder=='yzx':
      rotz = math.asin(-n.x)
      cz   = math.cos(rotz)
      rotx = SArcCos(n.y, cz)

      # Check Third Equation
      if math.fabs(n.z - math.sin(rotx)*cz) > FEPSILON:
        # Sign mismatch --> Use other arccos solution
        rotx = -rotx
    
    elif AxisOrder=='xyz':
      roty = - math.asin(n.z)
      cy   = math.cos(roty)
      rotz = SArcCos(n.x, cy)

      # Check Third Equation
      if math.fabs(n.y - math.sin(rotz)*cy) > FEPSILON:
        # Sign mismatch --> Use other arccos solution
        rotz = -rotz
    
    else: # 'zxy'
      rotx = - math.asin(n.y)
      cx   = math.cos(rotx)
      roty = SArcCos(n.z, cx)
      
      if math.fabs(n.x - math.sin(roty)*cx) > FEPSILON:
        roty = -roty # SArcSin(n.x, cx)
        
    # Convert Result un degree
    if inDegrees:
      rotx = math.degrees(rotx)
      roty = math.degrees(roty)
      rotz = math.degrees(rotz)

    return (rotx, roty, rotz)


  @classmethod
  def face_orientation(cls, vxtab:'list of Point3d', AxisOrder='xyz', inDegrees=False):
    ''' Compute the orientation of a face according to an Axis order (xyz, yzx, zxy).
    The face is defined by a list of Point3d
    The orientation is the set of rotations that aligns the first axis of the
    axis order on the face normal vector.
    
    Parameters
    ----------
    vxtab : list of Point3d
      Face definition. Shall have 3 points at least

    axisOrder : str, defaul 'xyz'
      Rotation order between 'xyz', 'yzx' and 'zxy'

    inDegrees : bool, default False
      if True returns the orientation in degrees
      else orientation is in radians

    Return
    ------
    Vector3d
      None if vxtab is empty or too small
    '''

    if not vxtab or len(vxtab)<3:
      return None
    
    fcenter, p1, p2 = vxtab[:3]
    
    # Try to be more accurate on non triangular faces
    if len(vxtab)>3:
      fcenter = Point3d.barycentre(vxtab)
      p1, p2 = vxtab[0], vxtab[1]
      v0 = Vector3d.AB(fcenter, p1)
      v1 = Vector3d.AB(fcenter, p2)
      # Compute a first normale to get a sign reference
      n0 = v0.cross(v1)
      
      # Look for a point with a maximum (and better) absolute 'sinus'
      bestnorm, maxs = n0, n0.norme2()
      for p in vxtab[2:]:
        v2 = Vector3d.AB(fcenter, p)
        pv = v0.cross(v2)
        
        n = pv.norme2()
        if n>maxs:
          p2 = p
          bestnorm = pv
          maxs = n

      # If the best point generates a reserved normale, swap points order
      if n0.dot(bestnorm) < 0.0:
        p1, p2 = p2, p1
    
    # Perform the orientation computation  
    vr = Vector3d( Point3d.triangle_orientation(fcenter, p1, p2, AxisOrder=AxisOrder, inDegrees=inDegrees) )              
      
    return vr


  @classmethod
  def barycentre(cls, iterPt:'iterable of Point3d'):
    '''Compute the iso-barycenter of a set (or list) of Point3d.
    
    Parameters
    ----------
    iterPt: iterable of Point3d
    
    Return
    ------
    a Point3d with the expected center
    None if the input iterable is None or empty    
    '''
    if iterPt:
      b = Point3d()
      for p in iterPt:
        b.add(p)
      b.scale(1.0/len(iterPt))
      return b
    else:
      return None


  @classmethod
  def rotateAxis(cls, r, p, AxisOrder='xyz'):
    ''' Perform rotations defined in parameter 'r' according to 
    order given by AxisOrder.
    
    Parameters
    ----------
    r : Vector3d
      Rotation vector (RotX, RotY, RotZ)

    AxisOrder : str, defaul 'xyz'
      Rotation order between 'xyz', 'yzx' and 'zxy'

    Return
    ------
    Point3d
      Rotated element
    '''
    theta = r.x*math.pi/180.0
    c, s = math.cos(theta), math.sin(theta)
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0,   c, - s ], \
       [ 0.0,   s,   c ], \
       ]
  
    theta = r.y*math.pi/180.0
    c, s = math.cos(theta), math.sin(theta)
    MRotY = [ \
       [   c, 0.0,   s ], \
       [ 0.0, 1.0, 0.0 ], \
       [ - s, 0.0,   c ], \
       ]

    theta = r.z*math.pi/180.0
    c, s = math.cos(theta), math.sin(theta)
    MRotZ = [ \
      [   c, - s, 0.0], \
      [   s,   c, 0.0 ], \
      [ 0.0, 0.0, 1.0 ], \
      ]

    if AxisOrder=='xyz':
      m = MxProd(MRotY, MRotX)
      m = MxProd(MRotZ, m)
    elif AxisOrder=='yzx':
      m = MxProd(MRotZ, MRotY)
      m = MxProd(MRotX, m)
    else: # zxy
      m = MxProd(MRotX, MRotZ)
      m = MxProd(MRotY, m)

    return p.Lin33(m)

  # End of Class Point3d ======================================================


    
class Vector3d(Point3d):
  ''' 3D Vector based on Point3d, for __str__ specialization '''
  def __init__(self, x=0.0, y=0.0, z=0.0):
    super(Vector3d, self).__init__(x,y,z)

  def __str__(self, *args, **kwargs):
    return 'V({0:.6g},{1:.6g},{2:.6g})'.format(self.x, self.y, self.z)

  @classmethod
  def AB(cls, a:'Point3d', b:'Point3d', normalize=False):
    '''Convenience method to create a Vector3d from 2 Point3d.
    
    Parameters
    ----------
    a: First Point
    b: Second Point
    
    Return
    ------
    a Vector3d 
    '''
    return Vector3d( b.x-a.x, b.y-a.y, b.z-a.z ).normalize() if normalize else Vector3d( b.x-a.x, b.y-a.y, b.z-a.z )
  # End of Class Vector3d ======================================================
    

class TexCoord2f():
  ''' This class represent a (x,y) mutable tuple of float. '''

  def __init__(self, x=0.0, y=0.0):
    ''' Create a new TexCoord2f from various inputs.

    TexCoord2f() --> (0.0, 0.0)
    TexCoord2f(X,Y,Z as float) --> (X, Y)
    TexCoord2f(P as TexCoord2f) --> (p.x, p.y)
    TexCoord2f([X,Y]) --> ([0], [1], [2])

    Parameters
    ----------
    x : float (default 0.0) or Point3d or list or tuple
      X coordinate or global value if not float
    y : float (default 0.0)
      Y coordinate
    '''
    if isinstance(x, TexCoord2f):
      self.x = x.x 
      self.y = x.y 
    else:
      self.x = x 
      self.y = y 

  def add(self, v, v2=None):
    ''' Return if not v2 self+v else set self with v+v2 (to match javax.Vector3d behavior) '''
    if v2:
      if isinstance(v, TexCoord2f):
        self.x = v.x + v2.x
        self.y = v.y + v2.y
      else:
        self.x = v[0] + v2.x
        self.y = v[1] + v2.y
    else:
      if isinstance(v, TexCoord2f):
        self.x += v.x
        self.y += v.y
      else:
        self.x += v[0]
        self.y += v[1]

    return self
  
  def set(self, x=0.0, y=0.0):
    ''' Fill a TexCoord2f with various inputs.
    Arguments similar to __init__
    '''
    if isinstance(x, TexCoord2f):
      self.x = x.x 
      self.y = x.y 
    elif isinstance(x, float):
      self.x = x 
      self.y = y 
    else: # x is supposed to be a table of 3 floats
      self.x = x[0]
      self.y = x[1] 

    return self

  def scale(self, scalaire):
    ''' Multiply self by a scalar (float) '''
    self.x *= scalaire
    self.y *= scalaire
    return self

  def __str__(self, *args, **kwargs):
    return 'VT({0:g},{1:g})'.format(self.x, self.y)

  '''
  # Return if not v2 self - v
  #   else set current with v-v2 (to match javax.Vector3d)
  '''
  def sub(self, v, v2=None):
    ''' Return if not v2 self - v else set self with v-v2 (to match javax.Vector3d behavior) '''
    if v2:
      if isinstance(v, TexCoord2f):
        self.x = v.x - v2.x
        self.y = v.y - v2.y
      else:
        self.x = v[0] - v2.x
        self.y = v[1] - v2.y
    else:
      if isinstance(v, TexCoord2f):
        self.x -= v.x
        self.y -= v.y
      else:
        self.x -= v[0]
        self.y -= v[1]

    return self
  
  def __eq__(self, other):
    ''' Compare two TexCoord2f.

    Returns
    -------
    bool
      True if infinity-norm distance is smaller than FEPSILON
    '''
    return (math.fabs(other.x - self.x) < FEPSILON) and \
           (math.fabs(other.y - self.y) < FEPSILON)
  
  def __le__(self, other):
    return NotImplemented
  
  # End of Class TexCoord2f ====================================================
  

# =============================================================================#
# Library (more or less) internal functions                                    #
# =============================================================================#
# Code Cleaning
# def __isConvexXY(v0, v1):
#   v0.normalize()
#   v1.normalize()
#   return (v0.x*v1.y - v0.y*v1.x >= 0.0)
# 
# def isConvexXY(p00, p01, p10, p11):
#   s1 = __isConvexXY(Vector3d(p01.x-p00.x, p01.y-p00.y, 0.0), Vector3d(p11.x-p00.x, p11.y-p00.y, 0.0))
#   
#   return  s1==__isConvexXY(Vector3d(p10.x-p01.x, p10.y-p01.y, 0.0), Vector3d(p00.x-p01.x, p00.y-p01.y, 0.0)) and \
#     s1==__isConvexXY(Vector3d(p11.x-p10.x, p11.y-p10.y, 0.0), Vector3d(p01.x-p10.x, p01.y-p10.y, 0.0)) and \
#     s1==__isConvexXY(Vector3d(p00.x-p11.x, p00.y-p11.y, 0.0), Vector3d(p10.x-p11.x, p10.y-p11.y, 0.0)) 
# 
# def isRegular(p00, p01, p10, p11):
#   v0 = Vector3d(p01.x-p00.x, p01.y-p00.y, p01.z-p00.z).normalize()
#   v1 = Vector3d(p11.x-p00.x, p11.y-p00.y, p11.z-p00.z).normalize()
#   vn = v0.cross(v1)
#   
#   if vn.norme()<FEPSILON:
#     return False
# 
#   for a,b,c in [ (p10, p01, p00), ( p11, p10, p01), (p00, p11, p10) ]:
#     v0 = Vector3d(a.x-b.x, a.y-b.y, a.z-b.z).normalize()
#     v1 = Vector3d(c.x-b.x, c.y-b.y, c.z-b.z).normalize()
#     on = v0.cross(v1)
#     s = vn.dot(on)
#     if s<=0.4:
#       return False
# 
#   return True


def Regularity(p00, p01, p10, p11):
  ''' Compute a set of characterisation values on a Quadrangular face.

  Parameters
  ----------
  p00 : Point3d
    point of the face
  p01 : Point3d
    point of the face
  p10 : Point3d
    point of the face
  p11 : Point3d
    point of the face

  Returns
  -------
  float, int, float, int, Vector3d
    Minimum angle of edge angles and edge indice
    Minimum cosinus of edge normals to centrale normale and edge indice
    Centrale normale
  '''
  v0 = Vector3d(p10.x-p00.x, p10.y-p00.y, p10.z-p00.z).normalize()
  v1 = Vector3d(p11.x-p01.x, p11.y-p01.y, p11.z-p01.z).normalize()
  vn = v0.cross(v1)
    
  avgdz = (math.fabs(p00.z-p11.z) + math.fabs(p01.z-p10.z))/2.0
  avglXY = ( p01.dXY(p00) + p10.dXY(p11) ) / 2.0
  f = avglXY/avgdz
  
  amin = sys.float_info.max
  cmin = sys.float_info.max
  
  for i, (a,b,c) in enumerate([ (p01, p00, p11), (p10, p01, p00), ( p11, p10, p01), (p00, p11, p10) ]):
    v0 = Vector3d(a.x-b.x, a.y-b.y, f*(a.z-b.z)).normalize()
    v1 = Vector3d(c.x-b.x, c.y-b.y, f*(c.z-b.z)).normalize()
    on = v0.cross(v1)
    
    a = math.acos(v0.dot(v1))
        
    s = on.norme()

    if a<amin:
      amin = a
      idxamin = i
       
    if s>0.0:
      c = vn.dot(on.scale(1.0/s))
      if c<cmin:
        cmin = c
        idxcmin = i
    else: # Indicate that the face has a flat face (null angle)
      cmin = -sys.float_info.max
      idxcmin = i
            
  return amin, idxamin, cmin, idxcmin, vn

# Code Cleaning
# def SinusXY(p00, p01, p11):
#   v0 = Vector3d(p01.x-p00.x, p01.y-p00.y, 0.0)
#   v1 = Vector3d(p11.x-p00.x, p11.y-p00.y, 0.0)
#   v0.normalize()
#   v1.normalize()
#   return v0.x*v1.y - v0.y*v1.x

# ==============================================================================
# Edge Management
# ==============================================================================
class Edge(NamedTuple):
  ''' The class represents an edge, composed of 2 Point3d.
  The edge may also contains the indexes of the Point3d in a coordinate list.
  '''
  p0: Point3d
  p1: Point3d
  idx0: int = -1
  idx1: int = -1
  hasTexture: bool = False
 
  def hashCode(self):
    return (min(self.idx0, self.idx1) << 32) | max(self.idx0, self.idx1)

  def __eq__(self, other):
    ''' Compares two edges.
    Equal function supposes to work in an homogeneous environnement
    Either Edges are indexed (idx >=0)
    Either they are just based on Points (3D)
    '''
    if self.idx0>=0:
      return self.hashCode() == other.hashCode()
    else:
      return (self.p0 == other.p0) and (self.p1 == other.p1)

  def __str__(self):
    return 'Edge({0:d}, {1:d}, {2:s}, {3:s})'.format(self.idx0, self.idx1, str(self.p0), str(self.p1))
  
  def isNull(self):
    ''' Return True is points are identical w.r.t the infinity-norm distance. ''' 
    return (math.fabs(self.p0.x-self.p1.x) < FEPSILON) and  \
           (math.fabs(self.p0.y-self.p1.y) < FEPSILON) and  \
           (math.fabs(self.p0.z-self.p1.z) < FEPSILON)

  def norme(self):
    ''' Returns the length of the edge. '''
    return self.p0.distance(self.p1)


  def cross(self, other):
    ''' Returns the cross product of self x other edge. '''
    return Vector3d(self.p0.x-self.p1.x, self.p0.y-self.p1.y, self.p0.z-self.p1.z).cross(Vector3d(other.p0.x-other.p1.x, other.p0.y-other.p1.y, other.p0.z-other.p1.z))

  def intersect(self, other):
    ''' Compute Edge intersection.

    Returns
    -------
    int, float
      Return +inf if None
             -inf if superposed (colinear and crossing strict)
              t : the location of the intersection point
                  in the first edge (self)
      C_COLINEAR_CROSS   = 0x0041
      C_COLINEAR         = 0x0040
      C_NOT_COPLANAR     = 0x0020
      C_INTERSECT        = 0x0001
      C_ERROR if one of them is a null vector
    '''
    if self.isNull() or other.isNull():
      return C_ERROR, sys.float_info.max

    A = self.p0
    B = self.p1
    U = Vector3d(B.x-A.x, B.y-A.y, B.z-A.z)

    Q1 = other.p0
    Q2 = other.p1
    S = Vector3d(Q2.x-Q1.x, Q2.y-Q1.y, Q2.z-Q1.z)

    AC = Vector3d(Q1.x-A.x, Q1.y-A.y, Q1.z-A.z)
    vn = U.cross(S)
    r = vn.dot(AC)
    if r!=0.0: # Non co-planar
      return C_NOT_COPLANAR, sys.float_info.max

    elif vn.isNullProd(): # Parallel lines
      if U.cross(AC).isNullProd():
        n2 = U.norme2()
        up = AC.dot(U) / n2
        sa = Vector3d(Q2.x-A.x, Q2.y-A.y, Q2.z-A.z).dot(U) / n2
        return C_COLINEAR_CROSS if ((up>-FEPSILON) and (up<1+FEPSILON)) or ((sa>-FEPSILON) and (sa<1+FEPSILON)) else C_COLINEAR, up
      else:
        # Colinear without intersection
        return C_COLINEAR, sys.float_info.max

    n2 = U.norme2()
    a = U.dot(AC) / n2
    b = U.dot(S) / n2
    C = Vector3d(U).scale(b).sub(S)

    up = C.dot(Vector3d( Q1.x-(1-a)*A.x-a*B.x, Q1.y-(1-a)*A.y-a*B.y, Q1.z-(1-a)*A.z-a*B.z) )/ C.norme2()
    sa = a+up*b
 
    return C_INTERSECT, up if (up>-FEPSILON) and (up<1+FEPSILON) and (sa>-FEPSILON) and (sa<1+FEPSILON) else sys.float_info.max

  #
  #
  def isAligned(self, other):
    ''' Test if Edges are aligned

    Returns
    -------
    bool
      True if aligned
      False if not aligned or one of them is a null vector
    '''
    if self.isNull() or other.isNull():
      return False

    A = self.p0
    B = self.p1
    U = Vector3d(B.x-A.x, B.y-A.y, B.z-A.z)

    Q1 = other.p0
    Q2 = other.p1
    S = Vector3d(Q2.x-Q1.x, Q2.y-Q1.y, Q2.z-Q1.z)

    AC = Vector3d(Q1.x-A.x, Q1.y-A.y, Q1.z-A.z)
    vn = U.cross(S)
    r = vn.dot(AC)
    if (r==0.0) and vn.isNullProd() and U.cross(AC).isNullProd(): # Parallel lines
      n2 = U.norme2()
      up = AC.dot(U) / n2
      sa = Vector3d(Q2.x-A.x, Q2.y-A.y, Q2.z-A.z).dot(U) / n2
      return ((up>-FEPSILON) and (up<1+FEPSILON)) or ((sa>-FEPSILON) and (sa<1+FEPSILON))
      #else:
        # Colinear without intersection
        #return False

    return False

  # End of Class Edge ====================================================

#
#
def FaceNormalOrder(f, refNorm):
  ''' Check face vertex order (and change it) to match the given normal
  Edges may be recreated.

  Parameters
  ----------
  f : list of Edges
    The defined by an ordered list of Edges
  refNorm : Vector3d
    The Normal to respect

  Returns
  -------
  Vector3d
    The initial normal of the face
  '''
  if not f:
    return None
  
  # Compute Face isobarycenter
  fcent = Point3d()
  for e in f:
    fcent.add(e.p0)
  fcent.scale(1.0/float(len(f)))

  fnorm = Edge(fcent, f[0].p0).cross(f[0]).normalize()
  s = fnorm.dot(refNorm)
  if s<0.0: # Reverse the edge list
    f.reverse()
    f[:] = [ Edge(e.p1, e.p0) for e in f ]

  return fnorm


class Bounds():
  ''' Base abstract class for Bounding ''' 
  def __init__(self):
    pass

  def combine(self, p3d):
    pass

  def intersect(self, p3d):
    pass

class BoundingSphere(Bounds):
  ''' Spheric Bounding class ''' 

  def __init__(self, center, radius):
    ''' Create BoundingSphere from a center and a radius. '''
    self.center = center
    self.radius = radius

  def combine(self, p3d):
    ''' Extend the BoundingSphere to hold the given Point. '''
    self.radius = max(self.radius, self.center.distance(p3d))

  def intersect(self, p3d):
    ''' Returns True if the given Point belongs the BoundingSphere. '''
    return (self.radius+FEPSILON > self.center.distance(p3d))



class BoundingBox(Bounds):
  ''' Cubic Bounding class ''' 
  def __init__(self, minCorner, maxCorner):
    ''' Create BoundingBox from two corners (points). '''
    self.minCorner = minCorner
    self.maxCorner = maxCorner

  def combine(self, p3d):
    ''' Extend the BoundingBox to hold the given Point. '''
    self.minCorner.set( min(self.minCorner.x, p3d.x), min(self.minCorner.y, p3d.y), min(self.minCorner.z, p3d.z) )
    self.maxCorner.set( max(self.maxCorner.x, p3d.x), max(self.maxCorner.y, p3d.y), max(self.maxCorner.z, p3d.z) )

  def intersect(self, p3d):
    ''' Returns True if the given Point belongs the BoundingBox. '''
    return (p3d.x > self.minCorner.x-FEPSILON) and (p3d.x < self.maxCorner.x + FEPSILON) and \
           (p3d.y > self.minCorner.y-FEPSILON) and (p3d.y < self.maxCorner.y + FEPSILON) and \
           (p3d.z > self.minCorner.z-FEPSILON) and (p3d.z < self.maxCorner.z + FEPSILON)





# ------------------------------------------------------------------------------
# Utility geometrical functions
# ------------------------------------------------------------------------------


def LinePlaneInterSect(l1, l2, p1, p2, p3):
  ''' Compute the intersection of a segment with a plane.
  Line to Plane intersection - With a Plan defined by 3 points
  N = cross(P2-P1, P3 - P1)
  Answer = L1 + (dot(N, P1 - L1) / dot(N, L2 - L1)) * (L2 - L1)

  Raises a RuntimeError when the intersection does not exist

  Parameters
  ----------
  l1 : Point3d
    First Point of the segment
  l2 : Point3d
    Second Point of the segment
  p1 : Point2d
    Central point of the plane
  p2 : Point2d
    First point (Ox)
  p3 : Point2d
    Second point (Oy)

  Returns
  -------
  Point3d, float
    The Intersection point and the coordinate of this point the line (L1 L2)
  
  '''
  p2_p1 = Vector3d(p2).sub(p1) 
  p3_p1 = Vector3d(p3).sub(p1)
    
  n = p2_p1.cross(p3_p1)
  
  l2_l1 = Vector3d(l2).sub(l1) 
  det = n.dot(l2_l1)
  if math.fabs(det)<1e-8:
    raise RuntimeError("no intersection or line is within plane")
      
  k = n.dot(Vector3d(p1).sub(l1)) / det 
  return Vector3d(l1).add(l2_l1.scale(k)), k


# ----------------------------------------------------------------------------
def LineCoordInterSect(l1, l2, vnorm):
  ''' Compute the intersection of a segment with a plane of the Coordinate system.
  The plane contains the origin.
  function created for performance reasons.
  Answer = L1 + (dot(N, - L1) / dot(N, L2 - L1)) * (L2 - L1)
  Raises a RuntimeError when the intersection does not exist

  Parameters
  ----------
  l1 : Point3d
    First Point of the segment
  l2 : Point3d
    Second Point of the segment
  vnorm : Vector3d
    Normal the plane

  Returns
  -------
  Point3d, float
    The Intersection point and the coordinate of this point the line (L1 L2)
  
  '''
  l2_l1 = Vector3d(l2).sub(l1) 
  det = vnorm.dot(l2_l1)
  if math.fabs(det)<1e-8:
    raise RuntimeError("No intersection or line is within plane")
      
  k = vnorm.dot(Vector3d().sub(l1)) / det 
  return Vector3d(l1).add(l2_l1.scale(k)), k


def MxProd(X,Y):
  ''' Generic Matrix Product. '''
  return [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*Y)] for X_row in X]

def MxProdMatVect(X,Y):
  ''' Generic Matrix x Vector Product. '''
  return [ sum(a*b for a,b in zip(X_row,Y)) for X_row in X ] 

def Invert2x2(M):
  ''' Invert a 2x2 matrix and return a new 2x2 matrix. '''
  det = M[0][0]*M[1][1] - M[1][0]*M[0][1]
  return [ [  M[1][1]/det, -M[0][1]/det ], \
           [ -M[1][0]/det,  M[0][0]/det ] ] 


def d2XY(t0, t1):
  ''' Return Squared distance between t0 and t1 on the Oxy Plane.
  May be used for both Point3d, Vector3d and TexCoord2f
  '''
  return (t0.x - t1.x) * (t0.x - t1.x) + (t0.y - t1.y) * (t0.y - t1.y)



# MLS Estimation 
# public final static double suv(GMatrix Ap, Point3d puv)
def suv(Ap, puv):
  ''' Perform an MLS Estimation for a Point.
  Parameters
  ----------
  Ap : np.array
    Coef matrix
  puv : Point3d
    Point (in the SUV coord system) to estimate the altitude

  Returns
  -------
  float
    Altitude estimate
  '''
  return Ap[0][0] + Ap[1][0]*puv.x + Ap[2][0]*puv.y + Ap[3][0]*puv.x*puv.x + Ap[4][0]*puv.y*puv.y + Ap[5][0]*puv.x*puv.y



def CreateTransform(eu, ev):
  ''' Convenience function to create the third vector and the transform matrixes.
  Transformation Matrix for X --> U, Y --> V, Z --> W 
  '''
  # Compute the third axis of the coordinate system
  ew = eu.cross(ev).normalize()

  # Determine the Transformation Matrix for X --> U, Y --> V, Z --> W 
  M = [ \
      [ eu.x, eu.y, eu.z ], \
      [ ev.x, ev.y, ev.z ], \
      [ ew.x, ew.y, ew.z ], \
      ]
  
  # Inverse Matrix (transposed)
  MT = [ \
      [ eu.x, ev.x, ew.x ], \
      [ eu.y, ev.y, ew.y ], \
      [ eu.z, ev.z, ew.z ], \
      ]

  return ew, M, MT

# This method refers GeomGroup methods and should be implemented elsewhere
def CreatePlaneDef(planes, planeName, orientation='XZY'):
  ''' Find the center of the plane and the two vectors that define the plane '''
  plane = planes.getGroup(planeName)
  vxtab = plane.getFaceVertex(0)
  eu = Vector3d( vxtab[3].x - vxtab[0].x, vxtab[3].y - vxtab[0].y, vxtab[3].z - vxtab[0].z).normalize()
  ev = Vector3d( vxtab[1].x - vxtab[0].x, vxtab[1].y - vxtab[0].y, vxtab[1].z - vxtab[0].z).normalize()       
  center = Point3d(vxtab[3].x + vxtab[1].x, vxtab[3].y + vxtab[1].y, vxtab[3].z + vxtab[1].z).scale(0.5)
  
  return center, eu, ev





# ==============================================================================
# Coordinate System Management
# ==============================================================================
class CoordSyst:
 
  ''' 3D Coordinate System. 
  Attributs:
    center : Point3d
    eu, ev, ew : Vector3d
  '''
  
  def __init__(self, center, eu, ev):
    ''' Return a new coordinate system.

    Parameters
    ----------
    center : Point3d
      Center of the coordinate system in the 'origin' coord. system
    eu : Vector3d
      First vector of the base in the 'origin' coord. system
    ev : Vector3d
      Second vector of the base in the 'origin' coord. system
    '''
    self.center = center
    self.eu = eu
    self.ev = ev
    self.ew, self.M, self.MT = CreateTransform(eu, ev)
  
  def __str__(self):
    return 'C({0:s})-EU{1:s} - EV{2:s}'.format(str(self.center), str(self.eu), str(self.ev))
  
  def To(self, pOrLst, hasTexture=False):
    ''' Change p coordinates to this coordinate system.
      Allocate a new Point3d, a new Edge or a new list of each
    '''
    if isinstance(pOrLst, Point3d):
      
      p = Point3d(pOrLst).sub(self.center).inLin33(self.M)
      if hasTexture:
        p.texture = pOrLst.texture
        
      return p
    
    elif isinstance(pOrLst, Edge):
      p0 = Point3d(pOrLst.p0).sub(self.center).inLin33(self.M)
      p1 = Point3d(pOrLst.p1).sub(self.center).inLin33(self.M)

      if hasTexture:      
        p0.texture = pOrLst.p0.texture
        p1.texture = pOrLst.p1.texture

      return Edge(p0, p1, pOrLst.idx0, pOrLst.idx1)
    
    else: # pOrLst:
      # Use the first
      return [ self.To(el, hasTexture=hasTexture) for el in pOrLst ]


  def From(self, pOrLst, hasTexture=False):
    ''' Change p coordinates from this coordinate system to the original one
      Allocate a new Point3d
    '''
    if isinstance(pOrLst, Point3d):
      p = Point3d(pOrLst).inLin33(self.MT).add(self.center)
      if hasTexture:
        p.texture = pOrLst.texture
        
      return p
    
    elif isinstance(pOrLst, Edge):
      p0 = Point3d(pOrLst.p0).inLin33(self.MT).add(self.center)
      p1 = Point3d(pOrLst.p1).inLin33(self.MT).add(self.center)

      if hasTexture:      
        p0.texture = pOrLst.p0.texture
        p1.texture = pOrLst.p1.texture

      return Edge(p0, p1, pOrLst.idx0, pOrLst.idx1)
    
    else: # pOrLst:
      # Use the first
      return [ self.From(el, hasTexture=hasTexture) for el in pOrLst ]


  def inTo(self, pOrLst):
    ''' Change p coordinates to this coordinate system.
      Modify p
    '''
    if isinstance(pOrLst, Point3d):
      return pOrLst.sub(self.center).inLin33(self.M)
    else:
      return [ p.sub(self.center).inLin33(self.M) for p in pOrLst ]

  def inFrom(self, pOrLst):
    ''' Change p coordinates from this coordinate system to the original one
      Modify p
    '''
    if isinstance(pOrLst, Point3d):
      return pOrLst.inLin33(self.MT).add(self.center)
    else:
      return [ p.inLin33(self.MT).add(self.center) for p in pOrLst ]


  # -----------------------------------------------------------------------------
  def RadialScalePoint(self, coordList, k):
    ''' Perform a Radial Scaling in the Oxy plan the self Coord Syst on each point of the coordList
    Modify the original vertex inplace
    '''
    if (k==0.0) or (k==1.0): 
      return coordList
  
    # For each point in the upper cylinder : Do a radial quadratic scaling
    for p in coordList:
      # Change for Cutting Plan Coordinate System
      self.inTo(p)
      p.x *= k
      p.y *= k
      # Change (back) to initial Coordinate System
      self.inFrom(p)

    return coordList
    
  # -----------------------------------------------------------------------------
  def RadialScaleLoop(self, lstEdges, k):
    ''' Perform a Radial Scaling in the Oxy plan the self Coord Syst on each point of the edge list '''
    # Use local coordList
    coordList = [ ]
  
    for edge in lstEdges:      
      IndexAdd(coordList, edge[0])

    return self.RadialScalePoint(coordList, k)

  # -----------------------------------------------------------------------------
  def calcXYRadius(self, coordList):
    ''' Return the max of the Sqrt(x²+y²) if the self Coord Syst '''
    rmax = sys.float_info.min
    for p in coordList:
      # Change for Cutting Plan Coordinate System
      pcs = self.To(p)
  
      r = pcs.x*pcs.x + pcs.y*pcs.y
      if r>rmax:
        rmax = r

    return math.sqrt(rmax)
  
  # -----------------------------------------------------------------------------
  #
  def RadialQuadraticScaling(self, coordList, topRadius, dh=0.0, ds=0.0, topRep=None, radialLimit=0.0):
    ''' Perform a Radial Quadric Scaling in the self Coord Syst for each vertex of coordList
      The Parabol z = a.r² 
    - Modified Point are below the top Coord. Syst and z>0.0 in the (center, eu, ev) one
      The top Coord system is either given by topPlaneGrp of computed as follow:
      TopCoord = ( self.center + (0,0,dh), self.eu, self.ev )
    - And within a radialLimit (if not null)
    - Modify the input vertex

    Parameters
    ----------
    coordList : list of Point3d
      List of vertex to scale
    topRadius : float
      Radius of the parabol in dh
    dh : float
      Height limit of the Parabol
    ds : float
      Down limit of the Parabol
    topRep : CoordSyst
      Top Coordinate System. When null, 

    '''
    if not topRep:
      topRep = CoordSyst(Point3d(self.center).add(Vector3d(0.0, 0.0, dh).inLin33(self.MT)), self.eu, self.ev)
      
    ds = 0.25*dh if ds==0.0 else ds

    a = (dh+ds) / topRadius / topRadius
    rd2 = radialLimit*radialLimit
    
    # For each point in the upper cylinder and below the topPlane : Do a radial quadratic scaling
    for p in coordList:
      # In top the Coord Syst
      pInTop = topRep.To(p) # Point3d(p).sub(centerTop).inLin33(Mtop)
      if pInTop.z<=FEPSILON:
        # Change for Cutting Plan Coordinate System
        self.inTo(p)
        
        if (p.z>=-FEPSILON) and ((rd2==0.0) or (p.x*p.x+p.y*p.y < rd2)):
          k = math.sqrt( (p.z + ds) / a) / topRadius
          
          # p.scale(k) ==> Not Radial
          p.x *= k
          p.y *= k
      
        # Change (back) to initial Coordinate System
        self.inFrom(p) 
      

  # -----------------------------------------------------------------------------
  # - Points shall be below the top Coord. Syst
  # - And within a radialLimit (if not null)
  # - Modify the input vertex
  def RadialSplineScaling(self, coordList, topRadius, dh=0.0, ds=0.0, topRep=None, radialLimit=0.0, tabScale=None):
    ''' Perform a Radial Spline Scaling in the self Coord Syst

    - The scaling curve is defined by the point [-ds, 0] and the values of tabScale[]
      X coordinates of the tabScale values are dh / (len(tabScale)-1)
   
                                ^ Scale Ratio
                                |                           .....  X (usually 1.0 (100%))
                                |                .....   X
                                |        ..... X
                                |    ..X
                                |  .. 
                               .x..
                             .  |
                           .    |
                          .     |
                         .      |
      ------------------x-------|-----------------------------------|-------------->
                       -ds      |                                   dh
                                |        .....
    - Modified Point are below the top Coord. Syst and z>0.0 in the (center, eu, ev) one
      The top Coord system is either given by topPlaneGrp of computed as follow:
      TopCoord = ( self.center + (0,0,dh), self.eu, self.ev )
    - And within a radialLimit (if not null)
    - Modify the input vertex

    Parameters
    ----------
    coordList : list of Point3d
      List of vertex to scale
    topRadius : float
      Radius of the parabol in dh
    dh : float
      Height limit of the Parabol
    ds : float
      Down limit of the Parabol
    topRep : CoordSyst
      Top Coordinate System. When null, 

    '''
    if not topRep:
      topRep = CoordSyst(Point3d(self.center).add(Vector3d(0.0, 0.0, dh).inLin33(self.MT)), self.eu, self.ev)

      
    ds = 0.25*dh if ds==0.0 else ds
    
    rd2 = radialLimit*radialLimit
    
    nbSlice = len(tabScale)-1
    
    tabX = np.array( [ -ds, ] + [ float(i)*dh/float(nbSlice) for i in range(0,len(tabScale)) ])
    tabY = np.array( [ 0.0, ] + tabScale )
    tck = interpolate.splrep(tabX, tabY)
    
    # For each point in the upper cylinder and below the topPlane : Do a radial quadratic scaling
    for p in coordList:
      # In top the Coord Syst
      pInTop = topRep.To(p) # Point3d(p).sub(centerTop).inLin33(Mtop)
      if pInTop.z<=FEPSILON:
        # Change for Cutting Plan Coordinate System
        self.inTo(p)
          
        if (p.z>=-FEPSILON) and ((rd2==0.0) or (p.x*p.x+p.y*p.y < rd2)):
          k = interpolate.splev(p.z, tck, der=0)
          
          p.x *= k
          p.y *= k
      
        # Change (back) to initial Coordinate System
        self.inFrom(p) 
      


CuttingSit = collections.namedtuple('CutSit', ['pt', 'idx', 'loc'])
'''
  A CuttingSit represents the intersection of an edge of a polygone (a face) and a plane.
  pt : Point3d
    The intersection point
  idx : int
    the edge index (in the face)
  loc : int
    The intersection localisation : -1 ==> First Point, 0 ==> in (strict) the segment, 1 ==> The second point
'''

# -----------------------------------------------------------------------------
#
CuttingData = collections.namedtuple('CuttingData', ['grp', 'ogrp', 'rep', 'lstFacesIdx', 'nbFaces', 'hasTexture'])
'''
  Cut Data returned by the cut/slice/split/RadialScaleRemesh algorythms
  grp         : The created group (GeomGroup) - The top in cut operations
  ogrp        : The created group (GeomGroup) - The bottom in cut operations
  rep         : Coordinate System where cut operation were performed. Contains center, M, MT, eu, ev, ew
  lstFacesIdx : List of Faces Idx (List of List of int) of the cutting face
  hasTexture  : Indicates if textures were discovered and calculated
'''


#
# 
#
#
def CutEdges(lstEdgeVx, vnorm, hasTexture, radialLimit2):
  ''' Compute the intersection of a set of edges and a plan
  Parameters
  ----------
  lstEdgeVx : list of Edge or list of (Point3d, Point3d)
    the list of edges to cut
  vnorm :
    The direction of the normal of the cutting plane
  hasTexture : bool
    Indicate if the Point3d have embedded texture coordinates
  radialLimit2 : float
    Square of the radial limit
    When not null, an intersection point is kept if its distance to the origin 
    is smaller than radial limit

  Returns
  -------
  lstCutSit = [ ] of CutSit (Point3d, edgeIdx, -1|0|1, TextCoord2d)
  '''
  lstCutSit = [ ] # of CutSit (Point3d, edgeIdx, -1|0|1)
  edgeIdx = 0
  jumpLast = False
  jumpNext = False

  # for edgevx in lstEdgeVx:
  while edgeIdx < len(lstEdgeVx):
    edgevx = lstEdgeVx[edgeIdx]
    cuttingLoc = -2
    try:
      cutvx, k = LineCoordInterSect(edgevx[0], edgevx[1], vnorm)
      if (k>=-FEPSILON) and (k <= 1.0+FEPSILON) and ((radialLimit2==0.0) or (cutvx.norme2()<radialLimit2)):
        
        if cutvx == edgevx[0]:
          # The cutting point matches the first point of the edge
          # Ignore last edge
          cuttingLoc = 0
          cutvx = edgevx[0]
          jumpLast = (edgeIdx==0)
        elif cutvx == edgevx[1]:
          # The cutting point matches the second point of the edge
          # Ignore the next edge
          cuttingLoc = 1
          cutvx = edgevx[1]
          jumpNext = True
        else:
          cuttingLoc = -1

          # Compute VertTex (if any)
          if hasTexture:
            cutvx.texture = TexCoord2f( edgevx[0].texture.x + k*(edgevx[1].texture.x - edgevx[0].texture.x),  \
                                        edgevx[0].texture.y + k*(edgevx[1].texture.y - edgevx[0].texture.y))


        lstCutSit.append( CuttingSit(cutvx, edgeIdx, cuttingLoc) )
        
    except: # No intersection
      pass
    
    if jumpNext:
      edgeIdx += 2 
      jumpNext = False
    else:
      edgeIdx += 1 
      
    if (edgeIdx==len(lstEdgeVx)-1) and jumpLast:
      break
    # Next Edge

  return lstCutSit

 

def isFaceVisible(lstEdgeVx, vnorm):
  ''' Returns True if a face 'after' the plane following its normal
  Meaning that all points are visible
  vnorm est un des vecteurs de la base
  '''
  for e in lstEdgeVx:
    det = e[0].dot(vnorm)
    if det < 0.0: # At Least one point is not 'visible'
      return False

  return True

#
def FaceVisibility(lstEdgeVx, vnorm):
  '''Returns the minimum value of edge dot vnorm
  '''
  if lstEdgeVx:
    if isinstance(lstEdgeVx[0], Point3d):
      v = min( e.dot(vnorm) for e in lstEdgeVx )
    else:
      v = min( e[0].dot(vnorm) for e in lstEdgeVx )
  else:
    v=0.0
    
  return v


#------------------------------------------------------------------------------+
def TriangleCut(lstCutSit, lstEdgeVx, vnorm):
  ''' Cut a triangle and return the list of new faces and the created edge.
  Returns
  -------
  lstNewFaceVx, newEdge
  '''
  assert len(lstCutSit)==2, 'Invalid Cutting List:{0:s}'.format(lstCutSit)

  nf = None
  
  x0 = lstCutSit[0] # CutSit(pt, idx of the cut edge, loc)
  x1 = lstCutSit[1]
  p0 = lstEdgeVx[0][0]
  p1 = lstEdgeVx[1][0]
  p2 = lstEdgeVx[2][0]
  signP0 = (p0.dot(vnorm)>=0.0)

  if (x0.loc==-1) and (x1.loc==-1): # 2 new points (Big Case 1)
    #   
    #        p1---------p2   p1--x1---p2   p1--x0---p2
    #         |       /      |  .   ∕      |  .   ∕ 
    #         |      / ( 1)  | .   ∕ ( 2)  |   . ∕ ( 3)
    #         |     /        |.   ∕        |    x1    
    #         X0...X1        x0  ∕         |   /   
    #         |   /          |  ∕          |  ∕    
    #         |  /           | /           | /    
    #         | /            |/            |/    
    #        p0              p0            p0
    #
    # x0.idx   0             0             1
    # x1.idx   2             1             2

    # Must determine which face we keep
    if   x0.idx==0 and x1.idx==2:
      nf = [p0, x0.pt, x1.pt ] if signP0 else [x0.pt, p1, p2, x1.pt]

    elif x0.idx==0 and x1.idx==1:
      nf = [p0, x0.pt, x1.pt, p2 ] if signP0 else [x0.pt, p1, x1.pt]

    elif x0.idx==1 and x1.idx==2:
      nf = [p0, p1, x0.pt, x1.pt] if signP0 else [x0.pt, p2, x1.pt]

    #else: Impossible case

    newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)


    #   
    #        p1---x1----p2  p1=x0---p2     p1-----p2=x1
    #         |   .   /      |.     ∕      |    . ∕ 
    #         |  .   / (2.1) | .   ∕ (2.2) |  .  ∕ (2.3)
    #         |  .  /        |  . /        | .  /     
    #         | .  /         |   x1        x0  /   
    #         | . /          |  ∕          |  ∕    
    #         |. /           | /           | /    
    #         |./            |/            |/    
    #        p0=x0           p0            p0
    #
    # x0.loc   0             1             -1
    # x1.loc   -1            -1            1
    # x0.idx   0             0             0
    # x1.idx   1             2             1

  elif (x0.loc==0) and (x1.loc==-1) and (x1.idx==1): # Case 2.1
    signP2 = (p2.dot(vnorm)>=0.0)
    nf = [x0.pt, x1.pt, p2] if signP2 else [x0.pt, p1, x1.pt]
    newEdge = (x1.pt, x0.pt) if signP2 else (x0.pt, x1.pt)

  elif (x0.loc==1) and (x1.loc==-1) and (x1.idx==2): # Case 2.2
    signP2 = (p2.dot(vnorm)>=0.0)
    nf = [x1.pt, x0.pt, p2] if signP2 else [p0, x0.pt, x1.pt]
    newEdge = (x0.pt, x1.pt) if signP2 else (x1.pt, x0.pt)

  elif (x0.loc==-1) and (x1.loc==1): # Case 2.3
    nf = [p0, x0.pt, x1.pt] if signP0 else [x0.pt, p1, x1.pt]
    newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)

  else: # Cas tangent par un point ou un segment
    newEdge = [ ] if x0.pt==x1.pt else (x1.pt, x0.pt)
    if (p0.dot(vnorm)>=-FEPSILON) and  \
       (p1.dot(vnorm)>=-FEPSILON) and  \
       (p2.dot(vnorm)>=-FEPSILON):
      nf = [ p0, p1, p2 ]

  return nf, newEdge 
  


#  lstNewFaceVx, newEdge = QuadrangleCut(lstCutSit, lstEdgeVx)
def QuadrangleCut(lstCutSit, lstEdgeVx, vnorm):
  ''' Cut a quadrangular face and return the list of new faces and the created edge.
  Returns
  -------
  lstNewFaceVx, newEdge
  '''
  assert len(lstCutSit)==2, 'Invalid Cutting List:{0:s}'.format(lstCutSit)

  nf = None
  
  x0 = lstCutSit[0] # CutSit(pt, idx of the cut edge, loc)
  x1 = lstCutSit[1]

  p0 = lstEdgeVx[0][0]
  p1 = lstEdgeVx[1][0]
  p2 = lstEdgeVx[2][0]
  p3 = lstEdgeVx[3][0]
  
  signP0 = (p0.dot(vnorm)>=0.0)
  newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)

  if x0.loc==-1 and x1.loc==-1: # 2 new points (Big Case 1)
    #   
    #    p1--------------------p2    p1----X1--------------p2    p1--------------------p2
    #     |                     |     |   .                 |     |                     |
    #     |        ( 2)         |     |  .    ( 1)          |     |       ( 3)          |
    #     |                     |     | .                   |     |                     |
    #     X0....................X1    X0                    |    X0                     |
    #     |                     |     |                     |     | .                   |
    #     |                     |     |                     |     |  .                  |
    #     |                     |     |                     |     |   .                 |
    #    p0--------------------p3    p0--------------------p3     p0----x1--------------p3  
    #   
    # x0.idx        0                       0                       0
    # x1.idx        2                       1                       3
    #   
    #    p1--------X0----------p2    p1----------X0--------p2    p1--------------------p2
    #     |          .          |     |          .          |     |                     |
    #     |        (5).         |     |       (6).          |     |        (9)          |
    #     |            . .      |     |          .          |     |                     |
    #     |               . . . X1    |          .          |     |                     X0
    #     |                     |     |          .          |     |                   . |
    #     |                     |     |          .          |     |                  .  |
    #     |                     |     |          .          |     |                 .   |
    #    p0--------------------p3    p0----------X1--------p3    p0----------------X1--p3
    #   
    # x0.idx        1                         1                             2     
    # x1.idx        2                         3                             3

    # Must determine which face we keep
    for case in switch(3*x0.idx+x1.idx):
      if case(1):
        nf = [p0, x0.pt, x1.pt, p2, p3] if signP0 else [x0.pt, p1, x1.pt]
        break

      if case(2):
        nf = [p0, x0.pt, x1.pt, p3] if signP0 else [x0.pt, p1, p2, x1.pt]
        break

      if case(3):
        nf = [p0, x0.pt, x1.pt] if signP0 else [x0.pt, p1, p2, p3, x1.pt]
        break

      if case(5):
        nf = [p0, p1, x0.pt, x1.pt, p3] if signP0 else [x0.pt, p2, x1.pt]
        break

      if case(6):
        nf = [p0, p1, x0.pt, x1.pt] if signP0 else [x0.pt, p2, p3, x1.pt]
        break

      if case(9):
        nf = [p0, p1, p2, x0.pt, x1.pt] if signP0 else [x0.pt, p3, x1.pt]
        break
      
      if case():
        print('Impossible Case:'+str(3*x0.idx+x1.idx))
        break

  else:
    signP3 = (p3.dot(vnorm)>=0.0)
    
    for case in switch( (x0.loc, x1.loc, x0.idx, x1.idx) ):
    #   
    #    p1-------X1-----------p2    p1-------------------p2=X1  p1--------------------p2
    #     |      .              |     |                .    |     |                     |
    #     |     .  ( 1)         |     |       ( 2)  .       |     |       ( 3)          |
    #     |    .                |     |          .          |     |                     |
    #     |   .                 |     |        .            |     |             . . . . x1
    #     |  .                  |     |     .               |     |       . . .         |
    #     | .                   |     |  .                  |     |   . .               |
    #     |.                    |     |.                    |     | .                   |
    #   p0=X0------------------p3   p0=X0------------------p3   p0=X0-------------------p3  
    #   
    # x0.loc         0                           0                           0
    # x1.loc        -1                           1                          -1
    # x0.idx         0                           0                           0
    # x1.idx         1                           1                           2
      if case ( (0, -1, 0, 1) ):
        nf = [p0, x1.pt, p2, p3] if signP3 else [x0.pt, p1, x1.pt]
        newEdge = (x1.pt, x0.pt) if signP3 else (x0.pt, x1.pt)
        break
      if case ( (0,  1, 0, 1) ):
        nf = [p0, p2, p3] if signP3 else [p0, p1, p2]
        newEdge = (x1.pt, x0.pt) if signP3 else (x0.pt, x1.pt)
        break
      if case ( (0, -1, 0, 2) ):
        nf = [p0, x1.pt, p3] if signP3 else [x0.pt, p1, p2, x1.pt]
        newEdge = (x1.pt, x0.pt) if signP3 else (x0.pt, x1.pt)
        break
    #   
    #    p1-------------------p2=X1  p1--------------------p2
    #     |                     |     |                     |
    #     |        (4)          |     |       (5)           |
    #     |                     |     |                     |
    #    X0                     |     X0                    |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #    p0--------------------p3    p0-------------------p3=X1
    #   
    # x0.loc        -1                          -1
    # x1.loc         1                           1
    # x0.idx         0                           0
    # x1.idx         1                           2
      if case ( (-1, 1, 0, 1) ):
        nf = [p0, x0.pt, x1.pt, p3] if signP0 else [x0.pt, p1, p2]
        break

      if case ( (-1, 1, 0, 2) ):
        nf = [p0, x0.pt, p2, p3] if signP0 else [x0.pt, p1, p2]
        break
    #   
    #   p1=X0------------------p2   p1=X0------------------p2   p1=X0------------------p2
    #     |                     |     |                     |     |                     |
    #     |        (4)          |     |       (5)           |     |        (6)          |
    #     |                     |     |                     |     |                     |
    #     |                     X1    |                     |     |                     |
    #     |                     |     |                     |     |                     |
    #     |                     |     |                     |     |                     |
    #     |                     |     |                     |     |                     |
    #    p0--------------------p3    p0-------------------p3=X1  p0---------X1---------p3
    #   
    # x0.loc         1                           1                           1
    # x1.loc        -1                           1                          -1
    # x0.idx         0                           0                           0
    # x1.idx         2                           2                           3
      if case ( (1, -1, 0, 2) ):
        nf = [p0, x0.pt, x1.pt, p3] if signP0 else [x0.pt, p2, x1.pt]
        break

      if case ( (1, 1, 0, 2) ):
        nf = [p0, p1, p3] if signP0 else [p1, p2, p3]
        break

      if case ( (1, -1, 0, 3) ):
        nf = [p0, p1, x1.pt] if signP0 else [x0.pt, p2, p3, x1.pt]
        break
      
      if case ( (1, -1, 1, 2) ):
        nf = [p0, p1, x1.pt] if signP0 else [x0.pt, p2, p3, x1.pt]
        print("Yop:" + str(p0))
        break
    #   
    #    p1---------X0---------p2    p1-------------------p2=X0 
    #     |                     |     |                     |  
    #     |        (4)          |     |       (5)           | 
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #    p0-------------------p3=X1   p0-------X1----------p3
    #   
    # x0.loc        -1                           1
    # x1.loc         1                          -1
    # x0.idx         1                           1
    # x1.idx         2                           3
      if case ( (-1, 1, 1, 2) ):
        nf = [p0, p1, x0.pt, p3] if signP0 else [x0.pt, p2, p3]
        break

      if case ( (1, -1, 1, 3) ):
        nf =  [p0, p1, p2, x1.pt] if signP0 else [p2, p3, x1.pt]
        break

      if case( ): # Cas tangent par un point ou un segment
        if (p0.dot(vnorm)>=-FEPSILON) and  \
           (p1.dot(vnorm)>=-FEPSILON) and  \
           (p2.dot(vnorm)>=-FEPSILON) and \
           (p3.dot(vnorm)>=-FEPSILON):
          nf = [ p0, p1, p2, p3 ]
        
        # Create a new edge anyway
        newEdge = [ ] if x0.pt==x1.pt else newEdge
        break

  # return a face (cut) to add to the geometry and the new edge
  return nf, newEdge 

#
# Only Manage 3 and 4 edges faces
# Convex
#
def FaceCut34(lstEdgeVx, vnorm, hasTexture, radialLimit2):
  lstNewFaceVx = [ ]

  lstCutSit = CutEdges(lstEdgeVx, vnorm, hasTexture, radialLimit2)

  if len(lstCutSit)==0: # No valid Intersection - Face is // to the plane cute or Out the RadialLimit if any
    v = FaceVisibility(lstEdgeVx, vnorm)
    if v>FEPSILON:      
      # Determine if the face shall be kept
      lstNewFaceVx = [ v[0] for v in lstEdgeVx ]
      return lstNewFaceVx, [ ], False
    else:
      if (radialLimit2!=0.0) and (min( v[0].x*v[0].x+v[0].y*v[0].y for v in lstEdgeVx ) > radialLimit2):
        lstNewFaceVx = [ v[0] for v in lstEdgeVx ]
        return lstNewFaceVx, [ ], False
          
      #else:
      return [ ], [ ], False
    
  elif len(lstCutSit)==1: # Just one point of intersection
    # Determine if the face shall be kept
    if isFaceVisible(lstEdgeVx, vnorm):
      lstNewFaceVx = [ v[0] for v in lstEdgeVx ]      
      return lstNewFaceVx, [ ], False
    else:
      return [ ], [ ], False

  elif len(lstCutSit)==2: # Intersection not empty (and simple)
    # Differentiate Triangle and Quadrangle and Others
    if len(lstEdgeVx)==3:
      lstNewFaceVx, newEdge = TriangleCut(lstCutSit, lstEdgeVx, vnorm)
    else: # len(lstEdgeVx)==4:
      lstNewFaceVx, newEdge = QuadrangleCut(lstCutSit, lstEdgeVx, vnorm)
    # else: # No more possible triangularisation performed by FaceCut
    
  else: # More than two cut edges --> Don't manage it yet (Chevron)
    print("Face: has more than two cut edges:" + str(lstCutSit))
    # Keep the face
    lstNewFaceVx = [ Point3d(v[0]) for v in lstEdgeVx ]
    return lstNewFaceVx, [  ], False
    
  return lstNewFaceVx, [ newEdge ], False




#------------------------------------------------------------------------------+
#  lstNewFaceVx, newEdge = TriangleCut(lstCutSit, lstEdgeVx, Normale au Plan de coupe)
#
# Return 2 faces, 1 edge
#
def TriangleSlice(lstCutSit, lstEdgeVx, vnorm):

  assert len(lstCutSit)==2, 'Invalid Cutting List:{0:s}'.format(lstCutSit)

  nf1 = None
  nf2 = None
  
  x0 = lstCutSit[0] # CutSit(pt, idx of the cut edge, loc)
  x1 = lstCutSit[1]
  p0 = lstEdgeVx[0][0]
  p1 = lstEdgeVx[1][0]
  p2 = lstEdgeVx[2][0]
  signP0 = (p0.dot(vnorm)>=0.0)

  if (x0.loc==-1) and (x1.loc==-1): # 2 new points (Big Case 1)
    #   
    #        p1---------p2   p1--x1---p2   p1--x0---p2
    #         |       /      |  .   ∕      |  .   ∕ 
    #         |      / ( 1)  | .   ∕ ( 2)  |   . ∕ ( 3)
    #         |     /        |.   ∕        |    x1    
    #         X0...X1        x0  ∕         |   /   
    #         |   /          |  ∕          |  ∕    
    #         |  /           | /           | /    
    #         | /            |/            |/    
    #        p0              p0            p0
    #
    # x0.idx   0             0             1
    # x1.idx   2             1             2

    # Must determine which face we keep
    if   x0.idx==0 and x1.idx==2:
      nf1 = [p0, x0.pt, x1.pt ] 
      nf2 = [x0.pt, p1, p2, x1.pt]

    elif x0.idx==0 and x1.idx==1:
      nf1 = [p0, x0.pt, x1.pt, p2 ] 
      nf2 = [x0.pt, p1, x1.pt]

    elif x0.idx==1 and x1.idx==2:
      nf1 = [p0, p1, x0.pt, x1.pt]
      nf2 = [x0.pt, p2, x1.pt]

    #else: Impossible case

    newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)


    #   
    #        p1---x1----p2  p1=x0---p2     p1-----p2=x1
    #         |   .   /      |.     ∕      |    . ∕ 
    #         |  .   / (2.1) | .   ∕ (2.2) |  .  ∕ (2.3)
    #         |  .  /        |  . /        | .  /     
    #         | .  /         |   x1        x0  /   
    #         | . /          |  ∕          |  ∕    
    #         |. /           | /           | /    
    #         |./            |/            |/    
    #        p0=x0           p0            p0
    #
    # x0.loc   0             1             -1
    # x1.loc   -1            -1            1
    # x0.idx   0             0             0
    # x1.idx   1             2             1

  elif (x0.loc==0) and (x1.loc==-1) and (x1.idx==1): # Case 2.1
    signP2 = (p2.dot(vnorm)>=0.0)
    nf1 = [x0.pt, x1.pt, p2]
    nf2 = [x0.pt, p1, x1.pt]
    newEdge = (x1.pt, x0.pt) if signP2 else (x0.pt, x1.pt)

  elif (x0.loc==1) and (x1.loc==-1) and (x1.idx==2): # Case 2.2
    signP2 = (p2.dot(vnorm)>=0.0)
    nf1 = [p0, x0.pt, x1.pt]
    nf2 = [x1.pt, x0.pt, p2]
    newEdge = (x0.pt, x1.pt) if signP2 else (x1.pt, x0.pt)

  elif (x0.loc==-1) and (x1.loc==1): # Case 2.3
    nf1 = [p0, x0.pt, x1.pt]
    nf2 = [x0.pt, p1, x1.pt]
    newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)

  else: # Cas tangent par un point ou un segment
    newEdge = [ ] if x0.pt==x1.pt else (x1.pt, x0.pt)
    nf1 = [ p0, p1, p2 ]

  if not signP0:
    nf1, nf2 = nf2, nf1

  return nf1, nf2, newEdge 
  


#  lstNewFaceVx, newEdge = QuadrangleCut(lstCutSit, lstEdgeVx)
#
# Return 2 faces, 1 edge
#
def QuadrangleSlice(lstCutSit, lstEdgeVx, vnorm):

  assert len(lstCutSit)==2, 'Invalid Slicing List:{0:s}'.format(lstCutSit)

  nf1 = None
  nf2 = None
  
  x0 = lstCutSit[0] # CutSit(pt, idx of the cut edge, loc)
  x1 = lstCutSit[1]

  p0 = lstEdgeVx[0][0]
  p1 = lstEdgeVx[1][0]
  p2 = lstEdgeVx[2][0]
  p3 = lstEdgeVx[3][0]
  
  signP0 = (p0.dot(vnorm)>=-FEPSILON)
  newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)

  if x0.loc==-1 and x1.loc==-1: # 2 new points (Big Case 1)
    #   
    #    p1--------------------p2    p1----X1--------------p2    p1--------------------p2
    #     |                     |     |   .                 |     |                     |
    #     |        ( 2)         |     |  .    ( 1)          |     |       ( 3)          |
    #     |                     |     | .                   |     |                     |
    #     X0....................X1    X0                    |    X0                     |
    #     |                     |     |                     |     | .                   |
    #     |                     |     |                     |     |  .                  |
    #     |                     |     |                     |     |   .                 |
    #    p0--------------------p3    p0--------------------p3     p0----x1--------------p3  
    #   
    # x0.idx        0                       0                       0
    # x1.idx        2                       1                       3
    #   
    #    p1--------X0----------p2    p1----------X0--------p2    p1--------------------p2
    #     |          .          |     |          .          |     |                     |
    #     |        (5).         |     |       (6).          |     |        (9)          |
    #     |            . .      |     |          .          |     |                     |
    #     |               . . . X1    |          .          |     |                     X0
    #     |                     |     |          .          |     |                   . |
    #     |                     |     |          .          |     |                  .  |
    #     |                     |     |          .          |     |                 .   |
    #    p0--------------------p3    p0----------X1--------p3    p0----------------X1--p3
    #   
    # x0.idx        1                         1                             2     
    # x1.idx        2                         3                             3

    # Must determine which face we keep
    for case in switch(3*x0.idx+x1.idx):
      if case(1):
        nf1 = [p0, x0.pt, x1.pt, p2, p3] 
        nf2 = [x0.pt, p1, x1.pt]
        break

      if case(2):
        nf1 = [p0, x0.pt, x1.pt, p3]
        nf2 = [x0.pt, p1, p2, x1.pt]
        break

      if case(3):
        nf1 = [p0, x0.pt, x1.pt] 
        nf2 = [x0.pt, p1, p2, p3, x1.pt]
        break

      if case(5):
        nf1 = [p0, p1, x0.pt, x1.pt, p3]
        nf2 = [x0.pt, p2, x1.pt]
        break

      if case(6):
        nf1 = [p0, p1, x0.pt, x1.pt] 
        nf2 = [x0.pt, p2, p3, x1.pt]
        break

      if case(9):
        nf1 = [p0, p1, p2, x0.pt, x1.pt] 
        nf2 = [x0.pt, p3, x1.pt]
        break
      
      if case():
        print('Impossible Case:'+str(3*x0.idx+x1.idx))
        break
    
    # return the faces ordered by  sign P0
    if not signP0:
      nf1, nf2 = nf2, nf1
      
  else:
    signP3 = (p3.dot(vnorm)>=-FEPSILON2)
    
    for case in switch( (x0.loc, x1.loc, x0.idx, x1.idx) ):
    #   
    #    p1-------X1-----------p2    p1-------------------p2=X1  p1--------------------p2
    #     |      .              |     |                .    |     |                     |
    #     |     .  ( 1)         |     |       ( 2)  .       |     |       ( 3)          |
    #     |    .                |     |          .          |     |                     |
    #     |   .                 |     |        .            |     |             . . . . x1
    #     |  .                  |     |     .               |     |       . . .         |
    #     | .                   |     |  .                  |     |   . .               |
    #     |.                    |     |.                    |     | .                   |
    #   p0=X0------------------p3   p0=X0------------------p3   p0=X0-------------------p3  
    #   
    # x0.loc         0                           0                           0
    # x1.loc        -1                           1                          -1
    # x0.idx         0                           0                           0
    # x1.idx         1                           1                           2
      if case ( (0, -1, 0, 1) ):
        nf1 = [p0, x1.pt, p2, p3] 
        nf2 = [x0.pt, p1, x1.pt]
        if not signP3:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP3 else (x0.pt, x1.pt)
        break
      if case ( (0,  1, 0, 1) ):
        nf1 = [p0, p2, p3] 
        nf2 = [p0, p1, p2]
        if not signP3:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP3 else (x0.pt, x1.pt)
        break
      if case ( (0, -1, 0, 2) ):
        nf1 = [p0, x1.pt, p3] 
        nf2 = [x0.pt, p1, p2, x1.pt]
        if not signP3:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP3 else (x0.pt, x1.pt)
        break
    #   
    #    p1-------------------p2=X1  p1--------------------p2
    #     |                     |     |                     |
    #     |        (4)          |     |       (5)           |
    #     |                     |     |                     |
    #    X0                     |     X0                    |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #    p0--------------------p3    p0-------------------p3=X1
    #   
    # x0.loc        -1                          -1
    # x1.loc         1                           1
    # x0.idx         0                           0
    # x1.idx         1                           2
      if case ( (-1, 1, 0, 1) ):
        nf1 = [p0, x0.pt, x1.pt, p3] 
        nf2 = [x0.pt, p1, p2]
        if not signP0:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)
        break

      if case ( (-1, 1, 0, 2) ):
        nf1 = [p0, x0.pt, p3] 
        nf2 = [x0.pt, p1, p2, p3]
        if not signP0:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)
        break
    #   
    #   p1=X0------------------p2   p1=X0------------------p2   p1=X0------------------p2
    #     |                     |     |                     |     |                     |
    #     |        (4)          |     |       (5)           |     |        (6)          |
    #     |                     |     |                     |     |                     |
    #     |                     X1    |                     |     |                     |
    #     |                     |     |                     |     |                     |
    #     |                     |     |                     |     |                     |
    #     |                     |     |                     |     |                     |
    #    p0--------------------p3    p0-------------------p3=X1  p0---------X1---------p3
    #   
    # x0.loc         1                           1                           1
    # x1.loc        -1                           1                          -1
    # x0.idx         0                           0                           0
    # x1.idx         2                           2                           3
      if case ( (1, -1, 0, 2) ):
        nf1 = [p0, x0.pt, x1.pt, p3] 
        nf2 = [x0.pt, p2, x1.pt]
        if not signP0:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)
        break

      if case ( (1, 1, 0, 2) ):
        nf1 = [p0, p1, p3] 
        nf2 = [p1, p2, p3]
        if not signP0:
          nf1,nf2 = nf2,nf1
        
        newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)
        break

      if case ( (1, -1, 0, 3) ):
        nf1 = [x0.pt, p2, p3, x1.pt]
        nf2 = [p0, p1, x1.pt] 
        if not signP0:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)
        break
      
      if case ( (1, -1, 1, 2) ):
        nf1 = [p0, p1, x1.pt] 
        nf2 = [x0.pt, p2, p3, x1.pt]
        print("Yop:" + str(p0))
        break
    #   
    #    p1---------X0---------p2    p1-------------------p2=X0 
    #     |                     |     |                     |  
    #     |        (4)          |     |       (5)           | 
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #     |                     |     |                     |
    #    p0-------------------p3=X1   p0-------X1----------p3
    #   
    # x0.loc        -1                           1
    # x1.loc         1                          -1
    # x0.idx         1                           1
    # x1.idx         2                           3
      if case ( (-1, 1, 1, 2) ):
        nf1 = [p0, p1, x0.pt, p3] 
        nf2 = [x0.pt, p2, p3]
        if not signP0:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)
        break

      if case ( (1, -1, 1, 3) ):
        nf1 = [p0, p1, p2, x1.pt] 
        nf2 = [p2, p3, x1.pt]
        if not signP0:
          nf1, nf2 = nf2, nf1
        newEdge = (x1.pt, x0.pt) if signP0 else (x0.pt, x1.pt)
        break

      if case( ): # Cas tangent par un point ou un segment
        nf1 = [ p0, p1, p2, p3 ]
        v = FaceVisibility(nf1, vnorm)
        # Determine in which group the face shall be kept
        if (v<-FEPSILON2):
          nf1, nf2 = nf2, nf1
          #newEdge = []
         
        newEdge = (x1.pt, x0.pt) if v>=-FEPSILON2 else (x0.pt, x1.pt)
        # Create a new edge anyway
        newEdge = [ ] if x0.pt==x1.pt else newEdge
        return nf1, nf2, newEdge 

  # return a face (cut) to add to the geometry and the new edge
  return nf1, nf2, newEdge 


#
# Only Manage 3 and 4 edges faces
# Convex
#
# Return 2 faces, 1 edge
#
def FaceSlice34(lstEdgeVx, vnorm, hasTexture, radialLimit2):
  lstNewFaceVx = [ ]

  lstCutSit = CutEdges(lstEdgeVx, vnorm, hasTexture, radialLimit2)

  if len(lstCutSit)<2: # No valid Intersection
    # Keep the face as is
    lstNewFaceVx = [ v[0] for v in lstEdgeVx ]
    
    # Find in which group
    v = FaceVisibility(lstEdgeVx, vnorm)
    
    # Determine in which group the face shall be kept
    if (v>-FEPSILON) or \
        ((radialLimit2!=0.0) and (min( v[0].x*v[0].x+v[0].y*v[0].y for v in lstEdgeVx ) > radialLimit2)):
      return lstNewFaceVx, [ ], [ ], False
    else:
      return [], lstNewFaceVx, [ ], False

  elif len(lstCutSit)==2: # Intersection not empty (and simple)
    # Differentiate Triangle from Quadrangle
    if len(lstEdgeVx)==3:
      nf1, nf2, newEdge = TriangleSlice(lstCutSit, lstEdgeVx, vnorm)
    else: # len(lstEdgeVx)==4:
      nf1, nf2, newEdge = QuadrangleSlice(lstCutSit, lstEdgeVx, vnorm)
    # else: # No more possible triangularisation performed by FaceCut
    
  else: # More than two cut edges --> Don't manage it yet (Chevron)
    print("Face: has more than two cut edges:" + str(lstCutSit))
    # Keep the face
    lstNewFaceVx = [ Point3d(v[0]) for v in lstEdgeVx ]
    return lstNewFaceVx, [ ], [  ], False
    
  return nf1, nf2, [ newEdge ], False



# -----------------------------------------------------------------------------
#
def FaceCut(lstEdgeVx, vnorm, hasTexture, slicing, radialLimit2):
  ''' Cut a face into 2 faces - Return the upper face along vnorm vector
  Return 1 list of list of Vertex and 1 list of edges
  '''
  nbEdges = len(lstEdgeVx)
  
  lstOflstFace = None

  if (nbEdges==3) or (nbEdges==4):
    if slicing:
      nf1, nf2, newEdge, *_ = FaceSlice34(lstEdgeVx, vnorm, hasTexture, radialLimit2)
      return [nf1, nf2], newEdge, True
    else:
      return FaceCut34(lstEdgeVx, vnorm, hasTexture, radialLimit2)

  elif (nbEdges==5) or (nbEdges==6):
    cutidx = 2 if nbEdges==5 else 3
    if slicing:
      nfl1, nfl2, leftEdge, *_ = FaceSlice34(lstEdgeVx[0:cutidx] + [ ( lstEdgeVx[cutidx-1][1], lstEdgeVx[0][0] ) ], vnorm, hasTexture, radialLimit2)
      nfr1, nfr2, rightEdge, *_ = FaceSlice34([ ( lstEdgeVx[0][0], lstEdgeVx[cutidx-1][1] ) ] + lstEdgeVx[cutidx:], vnorm, hasTexture, radialLimit2)
      lstOflstFace = [ nfl1, nfl2, nfr1, nfr2 ]
      
    else:
      leftFace, leftEdge, *_ = FaceCut34(lstEdgeVx[0:cutidx] + [ ( lstEdgeVx[cutidx-1][1], lstEdgeVx[0][0] ) ], vnorm, hasTexture, radialLimit2)
      rightFace, rightEdge, *_ = FaceCut34([ ( lstEdgeVx[0][0], lstEdgeVx[cutidx-1][1] ) ] + lstEdgeVx[cutidx:], vnorm, hasTexture, radialLimit2)
      lstOflstFace = [ leftFace, rightFace ]

  else: # nbEdges > 6
    mid = int(nbEdges / 2)
    leftFace, leftEdge, mleft = FaceCut(lstEdgeVx[0:mid] + [ ( lstEdgeVx[mid-1][1], lstEdgeVx[0][0] ) ], vnorm, hasTexture, slicing, radialLimit2)
    rightFace, rightEdge, mright = FaceCut([ ( lstEdgeVx[0][0], lstEdgeVx[mid-1][1] ) ] + lstEdgeVx[mid:], vnorm, hasTexture, slicing, radialLimit2)
    
    cas = 2*mleft + mright
    if cas==0:
      lstOflstFace = [ leftFace,  rightFace]
    elif cas==1:
      lstOflstFace = [ leftFace, ] + rightFace
    elif cas==2:
      lstOflstFace = leftFace + [ rightFace, ]
    else:
      lstOflstFace = leftFace + rightFace

  # Filter to remove empty face lists
  lstOflstFace = [l for l in lstOflstFace if l]

  return lstOflstFace, leftEdge+rightEdge, True

# -----------------------------------------------------------------------------
#
def FaceSplit(lstEdgeVx, vnorm, hasTexture, radialLimit2):
  ''' Split a face into 2 faces
  Return 2 lists of list of Vertex and 1 list of edges
  '''
  nbEdges = len(lstEdgeVx)

  if (nbEdges==3) or (nbEdges==4):
    nf1, nf2, newEdge, *_ = FaceSlice34(lstEdgeVx, vnorm, hasTexture, radialLimit2)
    return [nf1, ], [nf2, ], newEdge

  else: # if (nbEdges==5) or (nbEdges==6): else: # nbEdges > 6
    mid = int(nbEdges / 2)

    topFaces1, botFaces1, leftEdge = FaceSplit(lstEdgeVx[0:mid] + [ ( lstEdgeVx[mid-1][1], lstEdgeVx[0][0] ) ], vnorm, hasTexture, radialLimit2)

    topFaces2, botFaces2, rightEdge = FaceSplit([ ( lstEdgeVx[0][0], lstEdgeVx[mid-1][1] ) ] + lstEdgeVx[mid:], vnorm, hasTexture, radialLimit2)
    

  # Filter to remove empty face lists
  toplstOflstFace = [l for l in topFaces1+topFaces2 if l]
  botlstOflstFace = [l for l in botFaces1+botFaces2 if l]

  return toplstOflstFace, botlstOflstFace, leftEdge+rightEdge



#
# Check if the new edge does not cross a previously added edge
#
def canAddEdge(curFace, nedg, islast):
  for noedge, e in enumerate(curFace[1][:-1]):
    code, k = nedg.intersect(e)

    if (((noedge==0) and islast and (k==0.0)) or \
       ((k==sys.float_info.max)) and (code==C_INTERSECT)) or \
       (((noedge==0) and islast and (k==1.0) and (code==C_COLINEAR_CROSS))): 
      continue
    
    if (code==C_INTERSECT) or (code==C_COLINEAR_CROSS):
      return False

  return True

#Fast Edge Descriptror (mutable)
IDX0, IDX1, LSTNEXT, USED, CODE, COUNT = 0,1,2,3,4,5
#
# Edge Descriptor : [ idx0, idx1, List of nextEdgeIdx Ptr=[], used=False, code, count, ]


# ================================================================================================
# Compute the list of next Edges in the list of edges
# edgeIds is not in lstedidx anymore
#
def NextEdges(edgeIds, lstedidx):
  lstidx = [ ]

  # Map edges with their next edges - O(n)
  for j, nextEdgeIds in enumerate(lstedidx):
    # Avoid backward
    if (edgeIds[IDX1]==nextEdgeIds[IDX0]) and (edgeIds[IDX0]!=nextEdgeIds[IDX1]):
      lstidx.append(j)

  # Retry with reverted Edges
  for j, nextEdgeIds in enumerate(lstedidx):
    if ((edgeIds[IDX0]==nextEdgeIds[IDX0]) and (edgeIds[IDX1]!=nextEdgeIds[IDX1])) or \
        (edgeIds[IDX1]==nextEdgeIds[IDX1]) and (edgeIds[IDX0]!=nextEdgeIds[IDX0]):
      v = nextEdgeIds[IDX0]
      nextEdgeIds[IDX0] = nextEdgeIds[IDX1]
      nextEdgeIds[IDX1] = v
      lstidx.append(j)
      
  return lstidx


#
# Technical Exception to speed up result, when the result is optimal
class RecExit(Exception):
  pass


def CreateLoop(lstEdges):
  ''' Recursively create a set of faces from a set of edges.
  Use an min-max with alpha-beta prune
  An edge is represented by a tuple (p0,p1) of Point3d
  Texture coordinates are (if any) carried by an additionnal '.texture' attribut
  Return:
    The list of closed faces, the list Point3d, the number of edges in closed faces
  '''
  if not lstEdges:
    return [ ], [ ], 0
  
  # Use local coordList
  coordList = [ ]

  # Initialize the resolution system
  NewFaceLst = []
  BestFaceLst = []
  
  # EdgeStock is a list of Edge Descriptor [ idx0, idx1 ]
  EdgeStock = [ [ IndexAdd(coordList, edge[0]), IndexAdd(coordList, edge[1]) ] for edge in lstEdges ]      

  # Maximum Result : 1 face with all edges
  MaxScore = len(EdgeStock)

  def __Score(nfl):
    nbclosed = 0
    for f in nfl: nbclosed+=len(f[1])
    return nbclosed

  # Recursive method
  # TODO: Linearize the terminal recursion (for speed optim)
  #  Uses a alpha-beta prune based on NbFace of bestScore!!!
  #
  def __addEdge(NewFaceLst, curFacetpl, EdgeStock, curEdge, BestFaceLst, prof):
    if PYPOS3D_TRACE: print('__addEdge[{0:d}] Stock:{1:d}'.format(prof, len(EdgeStock)))
  
    #while EdgeStock:
    if not curEdge: # Get a new Edge from the stock
      curEdge = EdgeStock[0]
      del EdgeStock[0]
      startIdx = curEdge[IDX0]
  
    # If Current face exists      
    if curFacetpl:
      startIdx = curFacetpl[0]
    else:
      # Start a new Loop (face) rebuild
      curFacetpl = ( startIdx, [] )
  
    # Check if new edge is valid for the current face
    nedg = Edge(coordList[curEdge[IDX0]], coordList[curEdge[IDX1]])
    islast = (curEdge[IDX1]==startIdx)
    if canAddEdge(curFacetpl, nedg, islast):
      curFacetpl[1].append(nedg)
  
      # Check if the face is complete
      if islast:
        NewFaceLst.append(curFacetpl)
    
        if EdgeStock:
          # Try to create a new face, if the BestScore is lower than reachable one
          les = len(EdgeStock)

          nbclosed = __Score(NewFaceLst)
          bs = __Score(BestFaceLst)
          
          # if (les>2): # and (nbclosed+les>=__Score(BestFaceLst)) and (len(NewFaceLst)+1<len(BestFaceLst)):
          if (les>2) and ((nbclosed+les>=bs) or ((nbclosed+les==bs) and (len(NewFaceLst)+1<len(BestFaceLst)))):
            return __addEdge(NewFaceLst, None, EdgeStock, None, BestFaceLst, prof+1)
          else: # alpha-beta pruning
            # Return OK, because the last face was successful
            # But some edges can be consumed
            return nbclosed, C_OK

        else:
          # The Stock is empty (with a last successful face)
          # Compute the scoring of the solution
          nbclosed = __Score(NewFaceLst)
          if PYPOS3D_TRACE: print('__addEdge[{0:d}] Success:{1:d}'.format(prof, nbclosed))

          # Test if absolute best score has been reached
          if len(NewFaceLst)==1 and (nbclosed==MaxScore):
            BestFaceLst[:] = NewFaceLst[:]
            raise RecExit()

          return nbclosed, C_OK
        
      else: # Current face is not finished
        lstNextEd = NextEdges(curEdge, EdgeStock)
        if lstNextEd:
          bestScore, bestRes = __Score(BestFaceLst), C_ERROR
  
          for edgeIdx in lstNextEd:
            # Copy the 'gameplay'
            subFacetpl = ( curFacetpl[0], copy.copy(curFacetpl[1]) )
            subNewFaceLst = [ copy.copy(f) for f in NewFaceLst ]
            subEdgeStock = [ copy.copy(e) for e in EdgeStock ]
            nextEd = subEdgeStock[edgeIdx]
           
            subEdgeStock.remove(nextEd)
            
            subScore, res = __addEdge(subNewFaceLst, subFacetpl, subEdgeStock, nextEd, BestFaceLst, prof+1)
            
            if (subScore>bestScore) or ((subScore==bestScore) and (len(subNewFaceLst) < len(BestFaceLst))):
              bestScore, bestRes = subScore, res
              BestFaceLst[:] = subNewFaceLst[:]
              #print('BestScore.__addEdge[{0:d}]:{1:d} {2:d} faces'.format(prof, subScore, len(subNewFaceLst)))

              # Test if absolute best score has been reached
              if len(BestFaceLst)==1 and (bestScore==MaxScore):
                raise RecExit()

          # Keep the best face list (other discarded)
          NewFaceLst[:] = BestFaceLst[:]

          return bestScore, bestRes
  
        else: # The current Edge has no follower --> Open Face is dropped
          # Try with a new face (if we have some edges to consum)
          if EdgeStock:
            if PYPOS3D_TRACE: print('__addEdge[{0:d}] Dropping1'.format(prof))
            # Try to create a new face, if the BestScore is lower than reachable one
            les = len(EdgeStock)

            nbclosed = __Score(NewFaceLst)

            if (les>2): # and (nbclosed+les>=__Score(BestFaceLst)) and (len(NewFaceLst)+1<len(BestFaceLst)):
              return __addEdge(NewFaceLst, None, EdgeStock, None, BestFaceLst, prof+1)
            else: # alpha-beta pruning
              return nbclosed, C_FAIL

          else:
            # The Stock is empty (with a last unsuccessful face)
            # Compute the scoring of the solution
            nbclosed = __Score(NewFaceLst)
            if PYPOS3D_TRACE: print('__addEdge[{0:d}] Success2:{1:d}'.format(prof, nbclosed))
            return nbclosed, C_OK
  
            
    else: # Invalid choice --> Open Face is dropped
      # Try with a new face
      if EdgeStock:
        if PYPOS3D_TRACE: print('__addEdge[{0:d}] Dropping2'.format(prof))
        # Try to create a new face, if the BestScore is lower than reachable one
        les = len(EdgeStock)

        nbclosed = __Score(NewFaceLst)
        bs = __Score(BestFaceLst)

        if (les>2) and ((nbclosed+les>=bs) or ((nbclosed+les==bs) and (len(NewFaceLst)+1<len(BestFaceLst)))):
          return __addEdge(NewFaceLst, None, EdgeStock, None, BestFaceLst, prof+1)
        else: # alpha-beta pruning
          return nbclosed, C_FAIL

      else:
        # The Stock is empty (with a last unsuccessful face)
        # Compute the scoring of the solution
        nbclosed = __Score(NewFaceLst)
        if PYPOS3D_TRACE: print('__addEdge[{0:d}] Success3:{1:d}'.format(prof, nbclosed))
        return nbclosed, C_OK
  

  # Start the recursion
  try:
    score, res = __addEdge(NewFaceLst, None, EdgeStock, None, BestFaceLst, 0)
    if PYPOS3D_TRACE: print('CreateLoop({0:d}): score={1:d} res={2:d} NbFaces={3:d}'.format(len(lstEdges), score, res, len(NewFaceLst)))
    
  except RecExit:
    NewFaceLst = BestFaceLst
    score = __Score(BestFaceLst)
    if PYPOS3D_TRACE: print('CreateLoop({0:d}): Abs Best score={1:d} NbFaces={2:d}'.format(len(lstEdges), score, len(BestFaceLst)))
      
  # Return the list of created faces
  return [ FaceTpl[1] for FaceTpl in NewFaceLst ] if NewFaceLst else [], coordList, score


#------------------------------------------------------------------------------
def calcMLS(edgeSamp, startIdx, nbPt, edgeLoop, alpha):
  ''' Calculate "height" of vertex projected on a UV plane.
    
  Parameters
  ----------
  edgeSamp : list of Point3d
    UV projected Vertex. Z coordinate of each considered vertex
    will be affected with a height calculated with the MLS method.
   startIdx : int
     First vertex in edgeSamp to calculate
   nbPt : int
     Number of vertex to consider
   edgeLoop : list of Point3d
     The vertex at the vicinity of the hole
   alpha : float
     Influence of distant point (less than one).
  '''
  # Prepare the B matrix with edge loop vertex
  n = len(edgeLoop)
  # GMatrix B = new GMatrix(6, n);
  B = np.zeros((6, n))
  F = np.zeros((n, 1))
  # BT = np.zeros((n, 6))
  BWp = np.zeros((6, n))
  BWpBT =  np.zeros((6, 6))
  BWpBT1B = np.zeros((6, n))
  Ap = np.zeros((6, 1))

  for i in range(0,n):
    u = edgeLoop[i].x
    v = edgeLoop[i].y
    B[0][i] = 1.0
    B[1][i] = u
    B[2][i] = v
    B[3][i] = u * u
    B[4][i] = v * v
    B[5][i] = u * v

    F[i][0] = edgeLoop[i].z

  BT = B.transpose()
  Wp = np.zeros((n, n))

  for p in edgeSamp[startIdx:startIdx+nbPt]:
    # Calc W(p)  
    for j in range(0, n):
      d2jp = d2XY(p, edgeLoop[j])
      wjp = math.exp(-alpha * d2jp) / d2jp

      # 20081014 : Test of patch to avoid math errors.
      Wp[j][j] = 1.0 if math.isinf(wjp) or math.isnan(wjp) else wjp

    # Calculate a(p) = (B.Wp.Bt)-1 . B . Wp . F
    BWp = B.dot(Wp)
    BWpBT= BWp.dot(BT)
    try:
      #BWpBT = BWpBT.inv() # Mx 6x6
      BWpBT = np.linalg.inv(BWpBT) 
      BWpBT1B = BWpBT.dot(B) # // Mx 6xn 
      BWpBT1B = BWpBT1B.dot(Wp)
      Ap = BWpBT1B.dot(F)

      p.z = suv(Ap, p)
    except np.linalg.LinAlgError:
      print("Edge "+str(p)+" matrix non inv:" + str(BWpBT))
      
