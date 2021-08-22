#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "a python Quaternion module"#information describing the purpose of this module
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



class Quaternion:
	"""Quaternion class"""
	def __init__(self,x,y,z,w):
		self.x=x
		self.y=y
		self.z=z
		self.w=w
	
	def __mul__(self, other):
		""" comun """
		w = self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z
		x = self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y
		y = self.w*other.y + self.y*other.w + self.z*other.x - self.x*other.z
		z = self.w*other.z + self.z*other.w + self.x*other.y - self.y*other.x
		
		quaternion= Quaternion(x,y,z,w)
		quaternion= normalise(quaternion)
		return quaternion



### QUATERNION FUNCTIONS

def magnitude(quaternion):
	"""gives the magnitude of the quaternion"""
	return sqrt( quaternion.x**2 + quaternion.y**2 + quaternion.z**2 + quaternion.w**2 )


def normalise(quaternion):
	"""set quaternion magnitude equal to 1"""
	norm = magnitude(quaternion)
	quaternion = Quaternion( quaternion.x/norm,quaternion.y/norm,quaternion.z/norm,quaternion.w/norm )
	return quaternion


def from_axis_angle(axis,angle):
	"""The axis vector must be normalized,the angle is radians"""
	
	sin_angl = sin(angle / 2)
	cos_angl = cos(angle / 2)

	x = axis[0] * sin_angl
	y = axis[1] * sin_angl
	z = axis[2] * sin_angl
	w = cos_angl

	quaternion= Quaternion(x,y,z,w)
	return normalise(quaternion)


def get_axis_angle(quaternion):
	"""return axis as vector and the angle from the quaternion"""

	### quaternion normalization
	quaternion=normalise( quaternion )
	
	### get the angle of rotation
	angle = acos(quaternion.w) * 2 # * 180 / pi
	
	### get vector length from the axis components
	l= sqrt(sum([quaternion.x**2,quaternion.y**2,quaternion.z**2]))

	### normalise the axis vector
	axis = [quaternion.x/l,quaternion.y/l,quaternion.z/l]
	
	return axis,angle

