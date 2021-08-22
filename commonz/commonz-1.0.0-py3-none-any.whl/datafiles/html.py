#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "HTML Files Reading and Writing."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "1.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2020-06-20"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



#from html.parser import HTMLParser



def write_html_table(output_file,headers,lines):
	"""Write html table in output file"""
	with open(output_file,'w') as html_file :
		html_file.writelines("<table>\n")
		
		html_file.writelines("<thead><tr>\n")
		for field in headers :
			html_file.writelines("<th>{}</th>\n".format(field))
		html_file.writelines("</tr></thead>\n")
		
		html_file.writelines("<tbody>\n")
		for row in lines :
			html_file.writelines("<tr>\n")
			for data in row :
				lang_code=data['lang_code']
				dir=data['dir']
				text=data['text']
				html_file.writelines('<td lang="{}" dir="{}">{}</td>\n'.format(lang_code,dir,text))
			html_file.writelines("</tr>\n")
		html_file.writelines("</tbody>")
		
		html_file.writelines("</table>")
		
		
