#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



### XML = Extensible Markup Language



__doc__ = "XML files reading and writing."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "2.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2010"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



from xml.dom import minidom
#from xml.etree import ElementTree #Users who are not already proficient with the DOM should consider using this module instead.
#import xml.parsers.expat  #Fast XML parsing using Expat


def get(path,tag,attrib):
	"""return data from XML file"""
	db=[]
	xml_file = minidom.parse(path)
	parent= xml_file.firstChild
	for elm in parent.getElementsByTagName(tag) :
		db.append(elm.attributes[attrib].value)
	return db


def write_file(db,root_name,output_file):
	"""Write XML file from the given table"""
	doc = minidom.Document()
	root = doc.createElement(root_name)
	doc.appendChild(root)
	
	for e in db.keys() :
		#print(e)
		sub = doc.createElement(e)
		for a in db[e].keys() :
			#print(a)
			key=a
			valu=db[e][a]
			sub.setAttribute(key,valu)
			
		root.appendChild( sub )
	f=open(output_file,'wb')
	doc.writexml(f)
	f.close()
