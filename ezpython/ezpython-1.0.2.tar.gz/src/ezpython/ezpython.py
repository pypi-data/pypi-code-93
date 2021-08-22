def eTry(function):
	try:
		exec(function)
	except:
		return 'error'
	exec(function)
	
	
	
def isChinese(char):
	if '\u4e00' <= char <= '\u9fff':
		return True
	return False
	
	
	
def realLen(string):
	lenth=0
	for word in string:
		if isChinese(word):
			lenth+=2
		else:
			lenth+=1
	return lenth

	
			
def getRP():
	return '/sdcard/pydroid/'

def clr():
	import os
	os.system('clear')
	

		
def eReverse(list):
		result=[]
		for i in list:
			result.insert(0,i)
		return result
		
def dictSort(dict,valueSort=False):
	Rdict={}
	Rkeys=sorted([keys for keys in dict.keys()])
	Rvalues=sorted([values for values in dict.values()])
	for i in range(0,len(Rkeys)):
		if valueSort:
			Rdict[Rkeys[i]]=Rvalues[i]
		else:
			Rdict[Rkeys[i]]=dict[Rkeys[i]]
	return Rdict
	
def separation(char='*',output=True):
	string=''
	for _ in range(0,67):
		string+=char
	if output:
		print(string)
	return string

def getSimilarity(str1,str2):
	similarity=0
	eachSimilarity=int(100/len(str1))
	for word1 in str1:
		if word1 in str2:
			similarity+=eachSimilarity
		similarity-=3*abs(len(str1)-len(str2))
	if str1==str2:
		similarity=101
	return similarity
	
def printf(string,insert=' ',pos='left',customizeSuit=67,output=True):
	if pos=='left'or pos=='r':
		space=0
	elif pos=='middle'or pos=='m':
		space=int(customizeSuit/2-realLen(string))
	elif pos=='right'or pos=='r':
		space=customizeSuit-realLen(string)
	outputString=''
	if isChinese(insert):
		space=int(space/2)
	for _ in range(0,space):
		outputString+=insert
	outputString+=string
	leftSpace=customizeSuit-realLen(outputString)
	if isChinese(insert):
		leftSpace=int(leftSpace/2)
	for _ in range(0,leftSpace):
		outputString+=insert
	if output:
		print(outputString)
	return outputString
	
	
	
	
def enter(num=1):
	if num>=1:
		for _ in range(0,num):
			print('\n',end='')
	
if __name__=='__main__':
	import pysql.pysql as pysql
	document=pysql.BetterSql('documents')
	document.access('document')
	document.delete('/test')
	document.autoArrange()
	document.save()