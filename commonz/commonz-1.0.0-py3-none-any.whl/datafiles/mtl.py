#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "3D mtl file loader"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2010"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



def load_mtl_file(pathname):
	"""read 3D mtl file and return data"""
	mat_lib={}
	mat_file=open(pathname,'r')
	for line in mat_file.readlines() :
		if line.startswith('#'):
				continue
		data=string.split(line)
		if not len(data)==0 :
				signal=data[0]
				if signal=='newmtl' :
					name=data[1]
					material={}
					mat_lib[name]=material
				elif signal=='Ka' :
					ambient = map(float, values[1:])
					material["ambient"]=ambient
				elif signal=='Kd' :
					diffuse = map(float, values[1:])
					material["diffuse"]=diffuse
				elif signal=='Ks' :
					specular = map(float, values[1:])
					material["specular"]=specular
				elif signal== 'Ke':
					emissive = map(float, values[1:])
					material["emissive"]=emissive
				elif signal=='Ns' :
					shininess = float(values[1])
					material["highlight"]=shininess
				elif signal=='d' :
					opacity= float(data[1])
					material["halo"]=opacity
				elif signal=='illum' :
					illumin= float(data[1])
					material["illumination"]=illumin
				elif signal=='map_Kd' :
					textur=data[1]
					material["textur"]=textur
				else :
					warning("parse error : "+signal)

	mat_file.close()

	return mat_lib
