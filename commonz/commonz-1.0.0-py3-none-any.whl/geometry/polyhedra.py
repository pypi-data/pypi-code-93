#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "This module concern volumes."#information describing the purpose of this module
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
#import antiprism_python #  a collection of geometry 

from math import sqrt
from numpy import array



### ICOSAHEDRON
PHI = (sqrt(5) + 1) / 2
RAD = sqrt(PHI+2)
A = 1/RAD
B = PHI/RAD
ICO_VERTEX=[ (-A,0,B),(A,0,B),(-A,0,-B),(A,0,-B),(0,B,A),(0,B,-A),
(0,-B,A),(0,-B,-A),(B,A,0),(-B,A,0),(B,-A,0),(-B,-A,0) ]
ICO_FACES=[ (1,4,0),(4,9,0),(4,5,9),(8,5,4),(1,8,4),
(1,10,8),(10,3,8),(8,3,5),(3,2,5),(3,7,2),
(3,10,7),(10,6,7),(6,11,7),(6,0,11),(6,1,0),
(10,1,6),(11,0,9),(2,11,9),(5,2,9),(11,2,7) ]

### TETRAHEDRON
C=  1 / sqrt(3)
TETRA_VERTEX=[(-C,C,-C),(-C,-C,C),(C,C,C),(C,-C,-C)]
TETRA_FACES=[(0,2,1),(3,0,1),(3,1,2),(0,2,3)]



def normaliz(vector):
	long= sqrt( sum(vector**2) )
	return vector/long


def iterator(qantum,vertex_list,face_list):
	while qantum:
		new_face_list=[]
		for face in face_list :

			a=array(vertex_list[face[0]])
			b=array(vertex_list[face[1]])
			c=array(vertex_list[face[2]])
			
			na= tuple(normaliz( (a+b)/2. ))
			nb= tuple(normaliz( (b+c)/2. ))
			nc= tuple(normaliz( (c+a)/2. ))
			
			index=[]
			for v in [na,nb,nc] :
				if v in vertex_list :
					i=vertex_list.index(v)
					#print("in list")
				else :
					i=len(vertex_list)
					vertex_list.append(v)
				index.append(i)
			
			fa=(face[0],index[0],index[2])
			fb=(face[1],index[1],index[0])
			fc=(face[2],index[2],index[1])
			fd=(index[0],index[1],index[2])
			
			new_face_list.extend([fa,fb,fc,fd])
		face_list=new_face_list
		qantum-=1
	return vertex_list,tuple(face_list)
