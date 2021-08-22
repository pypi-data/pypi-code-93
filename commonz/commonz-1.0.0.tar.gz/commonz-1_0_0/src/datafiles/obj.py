#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "3D obj file loader"#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2010"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



def load_obj_file(filepath):
	"""read 3D obj file and return data"""
	#obj_file_list=[]
	objet={}
	vertex_list=[]
	vertice_list=[]
	normal_list=[]
	surface_mat={}
	group=''

	data_file=open(filepath,'r')
	for line in data_file.readlines() :
		if line.startswith('#'):
			continue
		data=string.split(line)
		if not len(data)==0 :
			signal=data[0]
			if signal=='v' :
					vertice_list.append( map(float, values[1:4]) )
			elif signal=='vt' :
					vertex_list.append( map(float, values[1:3])  )
			elif signal=='vn':
					normal_list.append( map(float, values[1:4]) )
			elif values[0] == 's':
					# smoothing-group not currently supported
					pass
			elif signal=='f' :
					a=map(int,string.split(data[1],'/'))
					b=map(int,string.split(data[2],'/'))
					c=map(int,string.split(data[3],'/'))
					face=(tuple(a),tuple(b),tuple(c))
					face_list.append(face)
			elif signal in ('usemtl', 'usemat') :
					material_name=data[1]
					if not surface_mat.has_key(material_name) :
						new_face_list=[]
						surface_mat[material_name]=new_face_list
					face_list=surface_mat[material_name]
			elif signal=='mtllib' :
					mat_lib=data[1]
			elif signal=='g' :
					group=data[1]
			elif signal=='o' :
					name=data[1]
			else :
					warning("signal inconu: "+signal)
	data_file.close()

	objet={
		"name":name,
		"group":group,
		"mat_lib":mat_lib,
		"vertex_list":vertex_list,
		"vertice_list":vertice_list,
		"normal_list":normal_list,
		"surface_mat":surface_mat
		}

	return objet


