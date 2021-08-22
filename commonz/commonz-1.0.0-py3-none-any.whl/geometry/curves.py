#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "This module concern curves."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
#__copyright__ = "Copyright 2000, The X Project"
__date__ = "2016"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



### import the required modules
from math import *
from numpy import array



### GET POINT

def get_spline4_point(control_a,point_b,point_c,control_d,t):
	"""gives the point t(between 0 and 1) on the defined spline curve"""
	a=(-control_a+3*point_b-3*point_c+control_d)/6
	b=(3*control_a-6*point_b+3*point_c)/6
	c=(-3*control_a+3*point_c)/6
	d=(control_a+4*point_b+point_c)/6
	return a*t**3+b*t**2+c*t+d

def get_bezier4_point(point_a,control_a,control_b,point_b,t):
	"""gives the point t(between 0 and 1) on the defined Bezier curve"""
	return (1-t)**3*point_a + 3*(1.-t)**2*t*control_a + 3*(1-t)*t**2*control_b + t**3*point_b

def get_bezier3w_point(point_a,point_b,point_c,w,t):
	"""gives the point t(between 0 and 1) on the defined bezier curve with w as point_b influence"""
	return (point_a*(1-t)**2+2*w*point_b*t*(1-t)+point_c*t**2)/((1-t)**2+2*w*t*(1-t)+t**2)

def get_bezier3_point(point_a,control,point_b,t):####
	"""gives the point t(between 0 and 1) on the defined curve"""
	a=(1-t)*point_b+t*control
	b=(1-t)*control+t*point_a
	diff=a-b
	long= sqrt( sum(diff**2) )
	normalized= diff/long
	return normalized



### GET POLYGON

def get_bezier3_polygon(point_a,control_b,point_c,definition):
	"""gives the polygon of the defined curve"""
	vertex_list=[]
	for increment in range(definition+1):
		t= increment/definition
		point= get_bezier3_point(point_a,control_b,point_c,t)
		vertex_list.append( point )
	return vertex_list
	
	
def get_bezier3w_polygon(point_a,control_b,point_c,w,definition):
	"""gives the polygon of the defined bezier curve with w as point_b influence"""
	vertex_list=[]
	for increment in range(definition+1):
		t= increment/definition
		point= get_bezier3w_point(point_a,control_b,point_c,w,t)
		vertex_list.append( point )
	return vertex_list
	
	
def get_bezier4_polygon(a,b,c,d,definition):
	"""gives the polygon of the defined bezier curve"""
	vertex_list=[]
	for increment in range(definition+1):
		t= increment/definition
		point= get_bezier4_point(a,b,c,d,t)
		vertex_list.append( point )
	return vertex_list


def get_spline4_polygon(control_a,point_b,point_c,control_d,definition):
	"""gives the polygon of the defined spline curve"""
	vertex_list=[]
	for increment in range(definition+1):
		t= increment/definition
		point= get_spline4_point(control_a,point_b,point_c,control_d,t)
		vertex_list.append( point )
	return vertex_list


def get_bezier_spline_polygon(point_a,point_b,point_c,point_d,definition):
	"""gives the polygon of the defined curve"""
	ta=1.0/3.0
	tb=2.0/3.0
	
	ab= (1-tb)*point_a+tb*point_b
	bc= (1-ta)*point_b+ta*point_c
	a= 0.5*ab+0.5*bc
	
	ca= (1-ta)*point_b+ta*point_c
	cb= (1-tb)*point_b+tb*point_c
	
	bc= (1-tb)*point_b+tb*point_c
	cd= (1-ta)*point_c+ta*point_d
	b= 0.5*bc+0.5*cd
	
	return get_bezier4_polygon(a,ca,cb,b,definition)



### curve length
def get_bezier3_length(point_a,control_b,point_c,precision):#
	"""approximate length of curve"""
	long=-1
	new_long=0
	definition=1
	while new_long-long>precision :
		long=new_long
		new_long=0
		definition*=2
		polygon= get_bezier3_polygon(point_a,control_b,point_c,definition)
		for index in range(len(polygon)-1):
			va=array(polygon[index])
			vz=array(polygon[index+1])
			v= vz-va
			l= sqrt( sum(v**2) )
			new_long+=l
		print(new_long)
	return long

