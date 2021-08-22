#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "python matrix module"#information describing the purpose of this module
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



### MATRIX CREATIONS
	
def get_3x3_identity():
	"""return 3x3 identity matrix"""
	a= [1.,0,0]
	b= [0,1.,0]
	c= [0,0,1.]
	return [a,b,c]
def get_4x4_identity():
	"""return 4x4 identity matrix"""
	a= [1.,0,0,0]
	b= [0,1.,0,0]
	c= [0,0,1.,0]
	d= [0,0,0,1.]
	return [a,b,c,d]

def get_4x4_projection_perspective(zc):
	"""return perspective projection 4x4 matrix"""
	a= [1,0,0,0]
	b= [0,1,0,0]
	c= [0,0,1,-1/zc]
	d= [0,0,0,1]
	return [a,b,c,d]
def get_4x4_projection_frustum(l,r,b,t,n,f):
	"""return matrix 4x4 same as glfrustum(l,r,b,t,n,f)"""
	a= [2*n/(r-l),0,0,0]
	b= [0,2*n/(t-b),0,0]
	c= [(r+l)/(r-l),(t+b)/(t-b),-(f+n)/(f-n),-1]
	d= [0,0,-2*f*n/(f-n),0]
	return [a,b,c,d]
def get_4x4_projection_ortho(l,r,b,t,n,f):
	"""return matrix 4x4 same as glortho(l,r,b,t,n,f)"""
	a= [2/(r-l),0,0,0]
	b= [0,2/(t-b),0,0]
	c= [0,0,-2/(f-n),0]
	d= [-(r+l)/(r-l),-(t+b)/(t-b),-(f+n)/(f-n),1]
	return [a,b,c,d]

def get_3x3_rotation_x(angle):
	"""return a 3x3 matrix for X axis rotation"""
	a= [1.,0.,0.]
	b= [0.,cos(angle),sin(angle)]
	c= [0.,-sin(angle),cos(angle)]
	return [a,b,c]
def get_3x3_rotation_y(angle):
	"""return a 3x3 matrix for Y axis rotation"""
	a= [cos(angle),0.,-sin(angle)]
	b= [0.,1.,0.]
	c= [sin(angle),0.,cos(angle)]
	return [a,b,c]
def get_3x3_rotation_z(angle):
	"""return a 3x3 matrix for Z axis rotation"""
	a= [cos(angle),sin(angle),0.]
	b= [-sin(angle),cos(angle),0.]
	c= [0.,0.,1.]
	return [a,b,c]

def get_3x3_rotation_axial(radian_angle,normalized_axis):
	"""return a 3x3 matrix for the axial rotation"""
	x=normalized_axis[0]
	y=normalized_axis[1]
	z=normalized_axis[2]
	c=cos(radian_angle)
	s=sin(radian_angle)
	a= [x**2+c*(1-x**2) , x*y*(1-c)-z*s , x*z*(1-c)+y*s]
	b= [x*y*(1-c)+z*s , y**2+c*(1-y**2) , y*z*(1-c)-x*s]
	c= [x*z*(1-c)-y*s , y*z*(1-c)+x*s , z**2+c*(1-z**2)]
	return [a,b,c]
def get_4x4_rotation_axial(radian_angle,normalized_axis):
	"""return a 4x4 matrix for the axial rotation"""
	x=normalized_axis[0]
	y=normalized_axis[1]
	z=normalized_axis[2]
	c=cos(radian_angle)
	s=sin(radian_angle)
	a= [x**2+c*(1-x**2) , x*y*(1-c)-z*s , x*z*(1-c)+y*s , 0]
	b= [x*y*(1-c)+z*s , y**2+c*(1-y**2) , y*z*(1-c)-x*s , 0]
	c= [x*z*(1-c)-y*s , y*z*(1-c)+x*s , z**2+c*(1-z**2) , 0]
	d= [ 0 , 0 , 0 , 1. ]
	return [a,b,c,d]

def get_3x3_homothety(x,y,z):
	"""return a homothety 3x3 matrix"""
	a= [x,0,0]
	b= [0,y,0]
	c= [0,0,z]
	return [a,b,c]
def get_4x4_homothety(x,y,z):
	"""return a homothety 4x4 matrix"""
	a= [x,0,0,0]
	b= [0,y,0,0]
	c= [0,0,z,0]
	d= [0,0,0,1]
	return [a,b,c,d]

def get_3x3_translation(x,y,z):
	"""return a matrix 3x3 for translation"""
	a= [x,0,0]
	b= [0,y,0]
	c= [0,0,z]
	return [a,b,c]
def get_4x4_translation(x,y,z):
	"""return a matrix 4x4 for translation"""
	a= [1,0,0,0]
	b= [0,1,0,0]
	c= [0,0,1,0]
	d= [x,y,z,1]
	return [a,b,c,d]



### MATRIX OPERATIONS

def product_3x3(b,a) :
	"""multiply two 3x3 matrices"""
	a1= a[0][0]*b[0][0]+a[0][1]*b[1][0]+a[0][2]*b[2][0]
	a2= a[0][0]*b[0][1]+a[0][1]*b[1][1]+a[0][2]*b[2][1]
	a3= a[0][0]*b[0][2]+a[0][1]*b[1][2]+a[0][2]*b[2][2]
	aa= [a1,a2,a3]
	b1= a[1][0]*b[0][0]+a[1][1]*b[1][0]+a[1][2]*b[2][0]
	b2= a[1][0]*b[0][1]+a[1][1]*b[1][1]+a[1][2]*b[2][1]
	b3= a[1][0]*b[0][2]+a[1][1]*b[1][2]+a[1][2]*b[2][2]
	bb= [b1,b2,b3]
	c1= a[2][0]*b[0][0]+a[2][1]*b[1][0]+a[2][2]*b[2][0]
	c2= a[2][0]*b[0][1]+a[2][1]*b[1][1]+a[2][2]*b[2][1]
	c3= a[2][0]*b[0][2]+a[2][1]*b[1][2]+a[2][2]*b[2][2]
	cc= [c1,c2,c3]
	return [aa,bb,cc]

def product_4x4(b,a) :
	"""multiply two 4x4 matrices"""
	a1= a[0][0]*b[0][0]+a[0][1]*b[1][0]+a[0][2]*b[2][0]+a[0][3]*b[3][0]
	a2= a[0][0]*b[0][1]+a[0][1]*b[1][1]+a[0][2]*b[2][1]+a[0][3]*b[3][1]
	a3= a[0][0]*b[0][2]+a[0][1]*b[1][2]+a[0][2]*b[2][2]+a[0][3]*b[3][2]
	a4= a[0][0]*b[0][3]+a[0][1]*b[1][3]+a[0][2]*b[2][3]+a[0][3]*b[3][3]
	aa= [a1,a2,a3,a4]
	b1= a[1][0]*b[0][0]+a[1][1]*b[1][0]+a[1][2]*b[2][0]+a[1][3]*b[3][0]
	b2= a[1][0]*b[0][1]+a[1][1]*b[1][1]+a[1][2]*b[2][1]+a[1][3]*b[3][1]
	b3= a[1][0]*b[0][2]+a[1][1]*b[1][2]+a[1][2]*b[2][2]+a[1][3]*b[3][2]
	b4= a[1][0]*b[0][3]+a[1][1]*b[1][3]+a[1][2]*b[2][3]+a[1][3]*b[3][3]
	bb= [b1,b2,b3,b4]
	c1= a[2][0]*b[0][0]+a[2][1]*b[1][0]+a[2][2]*b[2][0]+a[2][3]*b[3][0]
	c2= a[2][0]*b[0][1]+a[2][1]*b[1][1]+a[2][2]*b[2][1]+a[2][3]*b[3][1]
	c3= a[2][0]*b[0][2]+a[2][1]*b[1][2]+a[2][2]*b[2][2]+a[2][3]*b[3][2]
	c4= a[2][0]*b[0][3]+a[2][1]*b[1][3]+a[2][2]*b[2][3]+a[2][3]*b[3][3]
	cc= [c1,c2,c3,c4]
	d1= a[3][0]*b[0][0]+a[3][1]*b[1][0]+a[3][2]*b[2][0]+a[3][3]*b[3][0]
	d2= a[3][0]*b[0][1]+a[3][1]*b[1][1]+a[3][2]*b[2][1]+a[3][3]*b[3][1]
	d3= a[3][0]*b[0][2]+a[3][1]*b[1][2]+a[3][2]*b[2][2]+a[3][3]*b[3][2]
	d4= a[3][0]*b[0][3]+a[3][1]*b[1][3]+a[3][2]*b[2][3]+a[3][3]*b[3][3]
	dd= [d1,d2,d3,d4]
	return [aa,bb,cc,dd]

def substract_3x3(a,b) :
	""" substract the matrix3x3 A by the matrix3x3 B"""
	a1= a[0][0]-b[0][0]
	a2= a[0][1]-b[0][1]
	a3= a[0][2]-b[0][2]
	aa= [a1,a2,a3]
	b1= a[1][0]-b[1][0]
	b2= a[1][1]-b[1][1]
	b3= a[1][2]-b[1][2]
	bb= [b1,b2,b3]
	c1= a[2][0]-b[2][0]
	c2= a[2][1]-b[2][1]
	c3= a[2][2]-b[2][2]
	cc= [c1,c2,c3]
	return [aa,bb,cc]



### MATRIX VECTOR OPERATIONS

def product_3x3_vector3(matrix,vector):
	"""mulipli le vector 3 par une matrice care de 3"""
	x = matrix[0][0]*vector[0] + matrix[1][0]*vector[1] + matrix[2][0]*vector[2]
	y = matrix[0][1]*vector[0] + matrix[1][1]*vector[1] + matrix[2][1]*vector[2]
	z = matrix[0][2]*vector[0] + matrix[1][2]*vector[1] + matrix[2][2]*vector[2]
	return [x,y,z]

def product_vector3_3x3(vector,matrix):
	"""mulipli le vector par une matrice care """
	x = matrix[0][0]*vector[0] + matrix[0][1]*vector[1] + matrix[0][2]*vector[2]
	y = matrix[1][0]*vector[0] + matrix[1][1]*vector[1] + matrix[1][2]*vector[2]
	z = matrix[2][0]*vector[0] + matrix[2][1]*vector[1] + matrix[2][2]*vector[2]
	return [x,y,z]

def product_4x4_vector4(matrix,vector):
	"""mulipli  une matrice care de 4 par un vector de 4 par"""
	x = matrix[0][0]*vector[0] + matrix[1][0]*vector[1] + matrix[2][0]*vector[2] + matrix[3][0]*vector[3]
	y = matrix[0][1]*vector[0] + matrix[1][1]*vector[1] + matrix[2][1]*vector[2] + matrix[3][1]*vector[3]
	z = matrix[0][2]*vector[0] + matrix[1][2]*vector[1] + matrix[2][2]*vector[2] + matrix[3][2]*vector[3]
	w = matrix[0][3]*vector[0] + matrix[1][3]*vector[1] + matrix[2][3]*vector[2] + matrix[3][3]*vector[3]
	return [x,y,z,w]

def product_vector4_4x4(vector,matrix):
	"""mulipli le vector 4 par une matrice care de 4"""
	x = matrix[0][0]*vector[0] + matrix[0][1]*vector[1] + matrix[0][2]*vector[2] + matrix[0][3]*vector[3]
	y = matrix[1][0]*vector[0] + matrix[1][1]*vector[1] + matrix[1][2]*vector[2] + matrix[1][3]*vector[3]
	z = matrix[2][0]*vector[0] + matrix[2][1]*vector[1] + matrix[2][2]*vector[2] + matrix[2][3]*vector[3]
	w = matrix[3][0]*vector[0] + matrix[3][1]*vector[1] + matrix[3][2]*vector[2] + matrix[3][3]*vector[3]
	return [x,y,z,w]

