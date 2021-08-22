#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "a python vector module.shamely hacked from Alexander Pletzer code 5 Jan 00/11 April 2002"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
#__copyright__ = "Copyright 2000, The X Project"
__date__ = "2009-01"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
from math import *
from random import random



class Vector(tuple):
	"""a python vector class"""
	def size(self):
		return len(self)

	def __add__(self,other):
		"+"
		try:
			"self + other vector"
			return Vector( map(lambda s,o: s+o, self,other) )
		except:
			"self + other number"
			return Vector( map(lambda s: s+other, self) )
	def __radd__( self, other):
		""" other number + self"""
		return Vector( map(lambda s: other+s, self) )
	def __iadd__( self, other):
		" += "
		return self+other
	
	def __sub__(self, other):
		"-"
		try:
			"self - other vector"
			return Vector( map(lambda s,o: s-o, self,other) )
		except:
			"self - other number"
			return Vector( map(lambda s: s-other, self) )
	def __rsub__( self, other):
		" other number - self"
		return Vector( map(lambda s: other-s, self) )
	def __isub__( self, other):
		" -= "
		return self-other
	
	def __mul__(self, other):#manque pour matrix
		"*"
		try:
			"self * other vector"
			return Vector( map(lambda s,o: s*o, self,other) )
		except:
			"self * other number"
			return Vector( map(lambda s: s*other, self) )
	def __rmul__(self, other):
		" other number * self"
		return Vector( map(lambda s: other*s, self) )
	def __imul__( self, other) :
		" *= "
		return self*other

	def __div__(self, other):
		"/"
		try:
			"self / other vector"
			return Vector( map(lambda s,o: s/o, self,other) )
		except:
			"self / other number"
			return Vector( map(lambda s: s/other, self) )
	def __rdiv__(self, other):
		" other number / self"
		return Vector( map(lambda s: other/s, self) )
	def __idiv__( self, other) :
		" /= "
		return self/other

	def __truediv__( self, other):
		"truediv/"
		try:
			"self truediv/ other vector"
			return Vector( map(lambda s,o: s/o, self,other) )
		except:
			"self truediv/ other number"
			return Vector( map(lambda s: s/other, self) )
	def __rtruediv__( self, other):
		" other number truediv/ self"
		return Vector( map(lambda s: other/s, self) )
	def __itruediv__( self, other):
		"truediv/="
		return self/other

	def __floordiv__( self, other):
		"//"
		try:
			"self // other vector"
			return Vector( map(lambda s,o: s//o, self,other) )
		except:
			"self // other number"
			return Vector( map(lambda s: s//other, self) )
	def __rfloordiv__( self, other):
		" other number // self"
		return Vector( map(lambda s: other//s, self) )
	def __ifloordiv__( self, other):
		"//="
		return self//other
	
	def __mod__( self, other):
		"%"
		try:
			"self % other vector"
			return Vector( map(lambda s,o: s%o, self,other) )
		except:
			"self % other number"
			return Vector( map(lambda s: s%other, self) )
	def __rmod__( self, other):
		"nombre % self"
		return Vector( map(lambda s: other%s, self) )
	def __imod__( self,other):
		" %= "
		return self%other

	def __pow__( self, other):
		" ** "
		try:
			"self ** other vector"
			return Vector( map(lambda s,o: s**o, self,other) )
		except:
			"self ** other number"
			return Vector( map(lambda s: s**other, self) )
	def __rpow__( self, other):
		" other number ** self"
		return Vector( map(lambda s: other**s, self) )
	def __ipow__( self, other):
		" =** "
		return self**other

	def __neg__(self):
		" -self "
		return Vector( map(lambda s: 0-s, self) )
	def __pos__(self):
		" +self"
		return self
	def __abs__( self):
		" abs()"
		return Vector( map(lambda s: abs(s), self) )



### VECTORS FUNCTIONS

def direction(a,b):
	"""gives the vector from the first point to the second point"""
	return a-b

def vector_zeros(size):
	"Returns a vector of zeros"
	return Vector(map(lambda n: 0 , range(size)))
def vector_ones(size):
	" Returns a vector of ones "
	return Vector(map(lambda n: 1 , range(size)))
def vector_random(size, mini=-1.0, maxi=1.0):
	" Return a random vector"
	dif=maxi-mini
	return Vector( map(lambda n: random()*dif+mini ,range(size)) )

def length(vector):
	"""gives the length of the vector"""
	return sqrt( sum(vector**2) )
def normaliz(vector):
	"set vector length equal to 1"
	norm = length(vector)
	return Vector(  map( lambda n: n/norm , vector )  )
def scale(vector,mini_scale,maxi_scale):
	"""return a vector with values matching the interval of mini_scale maxi_scale"""
	offset=maxi_scale-mini_scale
	vector=normaliz(vector)*offset+mini_scale
	return Vector

def scalar_product(vector_a,vector_b):
	"""dot product of vectors a b (scalar product) dot(a,b)"""
	return sum(vector_a*vector_b)
def angle_between_vectors(vector_a,vector_b):
	"give the angle between the 2 vectors(no matter their length)."
	return acos( scalar_product( normaliz(vector_a),normaliz(vector_b) ) )
def angle_between_normalized_vectors(vector_normalized_a,vector_normalized_b):
	"give the angle between the 2 normalized vectors."
	return acos( scalar_product( vector_normalized_a,vector_normalized_b ) )
def check_same_direction(vector_a,vector_b):
	"""check if the two vectors point in the same direction, dot(a,b)=1"""
	if scalar_product(vector_a,vector_b)==1 :
		return True
	else :
		return False
def check_right_angle(vector_a,vector_b):
	"""check if the two vectors forms a right angle(90°), dot(a,b)=0"""
	if scalar_product(vector_a,vector_b)==0 :
		return True
	else :
		return False
def check_opposite_direction(vector_a,vector_b):
	"""check if the two vectors are opposite(angle of 180°), dot(a,b)=-1"""
	if scalar_product(vector_a,vector_b)==-1 :
		return True
	else :
		return False
def projection(vector_a,vector_b):
	"get the result of one vector projected on the other "
	a=scalar_product(vector_a,vector_b)
	b=scalar_product(vector_b,vector_b)
	return a/b*vector_b
def symmetrical_vector(vector,axis):
	"get the reflect of the given vector, from a symmetry axis"
	proj=projection(vector,axis)
	result = (proj-vector)*2+vector
	return result

def cross_product(vector_a,vector_b):
	"""gives a vector perpendicular to the plane formed by the two 3Dvectors"""
	return Vector([ vector_a[1]*vector_b[2]-vector_b[1]*vector_a[2] ,
						vector_b[0]*vector_a[2]-vector_a[0]*vector_b[2] ,
						vector_a[0]*vector_b[1]-vector_b[0]*vector_a[1] ])
def perpendicular_vector(vector_a,vector_b):
	"""gives a vector perpendicular to the plane formed by the two 3Dvectors"""
	return cross_product(vector_a,vector_b)



