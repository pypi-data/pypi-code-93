# package is called wday (Whirl Data is alternative to YAML)
import ast
from wday import *
from tkinter import ttk as QBSJFIWJFWOJWFJSONNWJLLGJEHGMICROSOFT
from tkinter import *
import os
import sys


class console:
	def put(args):
		return print(args)
	def get(args):
		return input(args)

class dictonary:
	def __init__(self,data):
		self.data = dict(data)
	def add(key,value):
		self.data[key] = value
	def remove(key):
		self.data[key] = ""
	def find(value):
		for xyz in self.data.keys():
			if self.data[xyz] == value:
				return xyz

class list:
	def __init__(self,data):
		self.data = list(data)
	def add(value):
		self.data.append(value)

def read(data):
	contents = {}
	contents['@'] = []
	for line in data.split("\n"):
		if line == "":
			continue
		elif line.isspace():
			continue
		elif line[0] == "~":
			continue
		elif line[0] == "@":
			contents['@'].append(line[1:])
		else:
			line = line[:-1]+"<<LINE-END>>"
			line.replace("\\::","|$?1?$|")
			line.replace("\\[","|$?2?$|")
			line.replace("\\]","|$?3?$|")
			contents[line[:line.find("::")]] = line[line.find("[")+len("["):line.find("<<LINE-END>>")]
			TEMP = contents[line[:line.find("::")]].split("::")
			contents[line[:line.find("::")]] = []
			for i in TEMP:
				i = i.replace("|$?1?$|","::")
				i = i.replace("|$?2?$|","[")
				i = i.replace("|$?3?$|","]")
				t1 = ast.literal_eval(i)
				contents[line[:line.find("::")]].append(t1)
			continue
	return contents

def script(file):
	try:
		QUBUFEZCHA = file[file.find("'''")+len("'''"):]
		BOLSHEVIEKSDEHS = file.find("'''")
		QEXNEKWMCNEOWJFNFNJWF = QUBUFEZCHA[:QUBUFEZCHA.find("'''")]
		init = read(file[:BOLSHEVIEKSDEHS])
		gui = QBSJFIWJFWOJWFJSONNWJLLGJEHGMICROSOFT
		exec(QEXNEKWMCNEOWJFNFNJWF)
	except:
		print('Script errored out.')