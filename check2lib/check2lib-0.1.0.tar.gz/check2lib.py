import requests
import os
import random
import string
import threading
from flask import Flask 
import colorama
import time
aloneeo= ""
def randomstring(string):
		alfabe = ["Q","W","E","R","T","Y","U","İ","O","P","A","S","D","F","G","H","J","K","L","Z","X","C","V","B","N","M","I"]
		alfabevesayilar = ["Q","W","E","R","T","Y","U","İ","O","P","A","S","D","F","G","H","J","K","L","Z","X","C","V","B","N","M","I","1","2","3","4","5","6","7","8","9","10"]
		sayilar = ["1","2","3","4","5","6","7","8","9","10"]
		a = random.choice(alfabe)
		b = random.choice(alfabevesayilar)
		c = random.choice(sayilar)
		string = string.replace("?s",a)
		string = string.replace("?m",b)
		string = string.replace("?n",c)
		return string

def addcombo(path):
        aloneeo= ""
        combos = open(str(path), encoding='utf8', errors = 'ignore').readlines()
        User = []
        Pass = []
        for y in combos:
            ez = y.replace("\n", "").split(":")
            try:
                User.append(ez[0])
                Pass.append(ez[1])
                print(ez[0]+":"+ez[1])
                time.sleep(1)
            except Exception as e:
                pass
        return User,Pass
def Parse(left,right,text):
	    koko216 = text.split(f'{left}')[1].split(f'{right}')[0] 
	    return str(koko216)
def htmlpages(htmlCode="<html><p>Html Code Boş bir değer taşıyor lütfen düzelt</p></html>"):
	app = Flask('')
	@app.route("/")
	def home():
		return htmlCode
	if __name__ =='librarydenemesi':
		app.run(debug=False)
	else:
		print(__name__)
