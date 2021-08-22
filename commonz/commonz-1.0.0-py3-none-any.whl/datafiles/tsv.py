#!/usr/bin/env python3
#coding: utf-8
### 1st line allows to execute this script by typing only its name in terminal, with no need to precede it with the python command
### 2nd line declaring source code charset should be not necessary but for exemple pydoc request it



__doc__ = "TSV File Reading and Writing."#information describing the purpose of this module
__status__ = "Development"#should be one of 'Prototype' 'Development' 'Production' 'Deprecated' 'Release'
__version__ = "3.0.0"# version number,date or about last modification made compared to the previous version
__license__ = "public domain"# ref to an official existing License
__date__ = "2015"#started creation date / year month day
__author__ = "N-zo syslog@laposte.net"#the creator origin of this prog,
__maintainer__ = "Nzo"#person who curently makes improvements, replacing the author
__credits__ = []#passed mainteners and any other helpers
__contact__ = "syslog@laposte.net"# current contact adress for more info about this file



import csv #CSV/TSV File Reading and Writing



DIALECT='unix-tsv'



### setting format
csv.register_dialect(DIALECT, delimiter='\t',quoting=csv.QUOTE_NONE,strict=True)



def get_table(tsv_path,fields_filter=[]):
	"""read TSV file and return database"""
	tabl=[]
	with open(tsv_path,newline='') as tsv_file :
		reader = csv.reader(tsv_file,dialect=DIALECT)
		for row in reader:
			#print(row)
			if row :
				tabl.append(row)
	
	tabl=tuple(zip(*tabl))
	#print(tabl)
	
	dico={}
	for column in tabl :
		header=column[0]
		data=column[1:]
		if not header in fields_filter :
			dico[header]=data
	return dico


def get_dico(tsv_path,fields_filter=[]):
	"""read TSV file and return dictionary"""
	db=[]
	with open(tsv_path,newline='') as tsv_file :
		reader = csv.DictReader(tsv_file,dialect=DIALECT)
		for row in reader:
			#print(row)
			for index in fields_filter :
				row.pop(index)
			#print(row)
			db.append(row)
	return db

	
def write_table(table,output_file):
	"""write TSV file from the given table"""
	with open(output_file,'w',newline='') as tsv_file :
		writer = csv.writer(tsv_file,dialect=DIALECT)
		
		h=[]
		db=[]
		for header in table.keys() :
			h.append(header)
			db.append(table[header])

		writer.writerow(h)
		for row in zip(*db) :
			#print(row)
			writer.writerow(row)


def write_dico(dico,output_file,head_field):
	"""write TSV file from the given dictionary"""
	with open(output_file,'w',newline='') as tsv_file :
		writer = csv.DictWriter(tsv_file,fieldnames=head_field,dialect=DIALECT)
		writer.writeheader()
		for data in dico :
			#print(data)
			writer.writerow(data)
